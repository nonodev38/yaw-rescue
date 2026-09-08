"""Network helpers and self-signed TLS certificate generation (étape P1.5).

Also hosts the plain-HTTP certificate download server that hands the .pem
file to phones so they can install it as a trusted CA before ever hitting
the HTTPS warning page.
"""
import http.server
import os
import socket
import threading
from pathlib import Path
from urllib.parse import urlparse

from deck.log import dlog


# ---------------------------------------------------------------------------
# Certificate download server — plain HTTP, so phones can fetch the CA cert
# and install it as trusted *before* ever hitting the HTTPS warning page.
# Some phones/OS network security policies (seen on Samsung) transparently
# force a TLS handshake even against a plain-HTTP port, so this is served on
# its own port purely to hand out the .pem file for install.
# ---------------------------------------------------------------------------
class CertHTTPHandler(http.server.BaseHTTPRequestHandler):
    cert_file = None

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")
        if path in ("", "/", "/cert", "/ca.pem"):
            try:
                data = Path(self.cert_file).read_bytes()
            except Exception as e:
                self.send_error(500, str(e))
                return
            self.send_response(200)
            # This MIME type makes Android offer to install the file as a
            # trusted CA certificate directly when downloaded.
            self.send_header("Content-Type", "application/x-x509-ca-cert")
            self.send_header("Content-Disposition", "attachment; filename=autoyawdeck-ca.pem")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        dlog("CERT-HTTP " + (fmt % args))


def start_cert_download_server(cert_file, port):
    handler = type("BoundCertHTTPHandler", (CertHTTPHandler,), {"cert_file": cert_file})
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


# ---------------------------------------------------------------------------
# Network helper
# ---------------------------------------------------------------------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_all_local_ips():
    """List every IPv4 address of this PC — a machine with several network
    adapters (Ethernet + Wi-Fi/hotspot) may need a different address per
    adapter depending on which network the phone is actually on."""
    ips = set()
    try:
        hostname = socket.gethostname()
        _, _, addrs = socket.gethostbyname_ex(hostname)
        ips.update(a for a in addrs if not a.startswith("127."))
    except Exception:
        pass
    ips.add(get_local_ip())
    return sorted(ips)


# ===========================================================================
#  SELF-SIGNED CERTIFICATE GENERATOR
#  Uses 'cryptography' library (already installed) for reliable cert creation.
# ===========================================================================

def generate_self_signed_cert(cert_dir):
    """Generate a self-signed SSL certificate automatically."""
    cert_dir = Path(cert_dir)
    cert_dir.mkdir(parents=True, exist_ok=True)
    cert_file = cert_dir / "server.pem"
    key_file = cert_dir / "server.key"

    if cert_file.exists() and key_file.exists():
        return str(cert_file), str(key_file)

    hostname = socket.gethostname()
    all_ips = get_all_local_ips()

    # Method 1: cryptography library (most reliable)
    try:
        return _generate_cert_cryptography(cert_file, key_file, hostname, all_ips)
    except ImportError:
        print("[Yaw Rescue] 'cryptography' library not found")
    except Exception as e:
        print(f"[Yaw Rescue] cryptography failed: {e}")

    # Method 2: openssl CLI
    try:
        return _generate_cert_openssl(cert_file, key_file, hostname, all_ips)
    except FileNotFoundError:
        print("[Yaw Rescue] 'openssl' not found in PATH")
    except Exception as e:
        print(f"[Yaw Rescue] openssl failed: {e}")

    print("[Yaw Rescue] No certificate method available!")
    print("  Install: pip install cryptography")
    print("  Or use:  python server.py --no-cert")
    return None, None


def _generate_cert_cryptography(cert_file, key_file, hostname, all_ips):
    """Generate cert using the 'cryptography' library."""
    import ipaddress as _ipaddress
    from datetime import datetime, timezone, timedelta
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    print("[Yaw Rescue] Generating RSA-2048 key pair...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    print("[Yaw Rescue] Building X.509 certificate...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])

    # Build SAN entries — include every local IP since a multi-homed PC may be
    # reached through a different network adapter than get_local_ip() guesses.
    san_list = [x509.DNSName(hostname), x509.DNSName("localhost")]
    san_list.append(x509.IPAddress(_ipaddress.ip_address("127.0.0.1")))
    for ip in all_ips:
        if ip and ip != "127.0.0.1":
            try:
                san_list.append(x509.IPAddress(_ipaddress.ip_address(ip)))
            except ValueError:
                pass

    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName(san_list), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    cert_file.write_text(
        cert.public_bytes(serialization.Encoding.PEM).decode("ascii"),
        encoding="utf-8",
    )
    key_file.write_text(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ).decode("ascii"),
        encoding="utf-8",
    )

    if os.name != "nt":
        os.chmod(str(key_file), 0o600)
    print(f"[Yaw Rescue] Certificate generated: {cert_file}")
    return str(cert_file), str(key_file)


def _generate_cert_openssl(cert_file, key_file, hostname, all_ips):
    """Fallback: generate cert using openssl CLI."""
    import subprocess

    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", str(key_file), "-out", str(cert_file),
        "-days", "365", "-nodes", "-subj", f"/CN={hostname}",
    ]
    # Add SAN if openssl supports -addext
    alt = f"DNS:{hostname},DNS:localhost,IP:127.0.0.1"
    for ip in all_ips:
        if ip and ip != "127.0.0.1":
            alt += f",IP:{ip}"
    try:
        subprocess.run(cmd + ["-addext", f"subjectAltName={alt}"],
                       capture_output=True, timeout=30, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(cmd, capture_output=True, timeout=30, check=True)

    if os.name != "nt":
        os.chmod(str(key_file), 0o600)

    print(f"[Yaw Rescue] Certificate generated: {cert_file}")
    return str(cert_file), str(key_file)

#!/usr/bin/env python3
"""
Auto-Yaw Deck — Local HTTPS server for X-Plane remote control.
Bridges the FlyWithLua auto_yaw script to a mobile web interface.

Usage:
    python server.py [--port 8443] [--cert-dir certs]
"""

import argparse
import datetime
import http.server
import io
import json
import os
import platform
import secrets
import socket
import ssl
import subprocess
import sys
import time
import threading
import traceback
from pathlib import Path
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Auto-install required packages
# ---------------------------------------------------------------------------
REQUIRED_PACKAGES = {
    'cryptography': 'cryptography',
    'qrcode': 'qrcode[pil]',
}

def ensure_packages():
    """Install missing Python packages automatically."""
    missing = []
    for module, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"[Auto-Yaw Deck] Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--quiet'] + missing,
                stdout=subprocess.DEVNULL if not os.environ.get('AYD_VERBOSE') else None,
                stderr=subprocess.DEVNULL if not os.environ.get('AYD_VERBOSE') else None,
            )
            print("[Auto-Yaw Deck] Packages installed successfully.")
        except subprocess.CalledProcessError:
            print("[Auto-Yaw Deck] WARNING: Some packages failed to install.")
            print("  Try manually: pip install cryptography qrcode[pil]")


ensure_packages()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_DIR = SCRIPT_DIR / "static"
DATA_DIR = SCRIPT_DIR / "data"
CERT_DIR = SCRIPT_DIR / "certs"

STATE_FILE = DATA_DIR / "state.txt"
COMMANDS_FILE = DATA_DIR / "commands.txt"


# ---------------------------------------------------------------------------
# Debug logging
# ---------------------------------------------------------------------------
def dlog(msg):
    """Debug logging — disabled to keep terminal clean under QR code."""
    pass

# ---------------------------------------------------------------------------
# State cache
# ---------------------------------------------------------------------------
state_cache = {}
state_lock = threading.Lock()

DEFAULT_STATE = {
    "bank_angle": "0.0", "yaw_rate": "0.0", "raw_input": "0.0",
    "final_output": "0.0", "smoothed_input": "0.0",
    "auto_coord_output": "0.0", "damper_output": "0.0",
    "enabled": "true", "smoothing_enabled": "true",
    "deadzone_enabled": "true", "auto_coord_enabled": "true",
    "yaw_damper_enabled": "true", "smoothing_factor": "0.15",
    "deadzone_size": "0.03", "auto_coord_gain": "0.40",
    "coord_bank_limit": "35.0", "damper_gain": "0.30",
    "damper_sensitivity": "2.0", "noise_filter": "0.05", "max_output": "1.0",
    "elevator_trim": "0.0", "aileron_trim": "0.0",
    "rudder_trim": "0.0", "flap_ratio": "0.0",
    "active_aircraft": "", "current_profile": "Default",
    "profiles": "", "timestamp": "0",
}


def read_state_file():
    data = dict(DEFAULT_STATE)
    if not STATE_FILE.exists():
        data["xplane_active"] = "false"
        return data
    try:
        for line in STATE_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                data[key.strip()] = value.strip()
    except Exception:
        pass
    # Detect if X-Plane is active: timestamp updated within last 5 seconds
    try:
        ts = int(data.get("timestamp", "0"))
        data["xplane_active"] = "true" if (time.time() - ts) < 5 else "false"
    except (ValueError, TypeError):
        data["xplane_active"] = "false"
    return data


def get_cached_state():
    with state_lock:
        return dict(state_cache)


def refresh_state():
    global state_cache
    state_cache = read_state_file()


def write_commands(lines):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(COMMANDS_FILE, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(line.strip() + "\n")
    except Exception as e:
        print(f"[Auto-Yaw Deck] Error writing commands: {e}")


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
        print("[Auto-Yaw Deck] 'cryptography' library not found")
    except Exception as e:
        print(f"[Auto-Yaw Deck] cryptography failed: {e}")

    # Method 2: openssl CLI
    try:
        return _generate_cert_openssl(cert_file, key_file, hostname, all_ips)
    except FileNotFoundError:
        print("[Auto-Yaw Deck] 'openssl' not found in PATH")
    except Exception as e:
        print(f"[Auto-Yaw Deck] openssl failed: {e}")

    print("[Auto-Yaw Deck] No certificate method available!")
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

    print("[Auto-Yaw Deck] Generating RSA-2048 key pair...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    print("[Auto-Yaw Deck] Building X.509 certificate...")
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

    print(f"[Auto-Yaw Deck] Certificate generated: {cert_file}")
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

    print(f"[Auto-Yaw Deck] Certificate generated: {cert_file}")
    return str(cert_file), str(key_file)


# ===========================================================================
#  HTTP Request Handler
# ===========================================================================

class DeckHTTPHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def setup(self):
        super().setup()
        dlog(f"Connection accepted from {self.client_address[0]}:{self.client_address[1]}")

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")
        dlog(f"GET {self.path} from {self.client_address[0]}")
        try:
            if path in ("", "/"):
                self._serve_main_page()
            elif path == "/api/state":
                refresh_state()
                self._serve_json(get_cached_state())
            elif path == "/api/qr":
                self._serve_qr()
            elif path == "/api/info":
                self._serve_json({"ip": get_local_ip(), "hostname": socket.gethostname(),
                                  "platform": platform.system()})
            elif path == "/api/health":
                self._serve_json({"status": "ok"})
            else:
                super().do_GET()
            dlog(f"GET {self.path} -> done")
        except (BrokenPipeError, ConnectionResetError) as e:
            dlog(f"GET {self.path} -> client disconnected: {e!r}")
        except Exception:
            dlog(f"GET {self.path} -> EXCEPTION:\n{traceback.format_exc()}")
            try:
                self.send_error(500, "Internal error (see server console)")
            except Exception:
                pass

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        dlog(f"POST {self.path} from {self.client_address[0]}")
        try:
            if path == "/api/command":
                self._handle_command()
            elif path == "/api/commands":
                self._handle_bulk_commands()
            else:
                self.send_error(404)
        except (BrokenPipeError, ConnectionResetError) as e:
            dlog(f"POST {self.path} -> client disconnected: {e!r}")
        except Exception:
            dlog(f"POST {self.path} -> EXCEPTION:\n{traceback.format_exc()}")
            try:
                self.send_error(500, "Internal error (see server console)")
            except Exception:
                pass

    def _handle_command(self):
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = json.loads(body.decode("utf-8"))
            lines = [f"set {k} {v}" if k != "_action" else f"action {v}"
                     for k, v in data.items()]
            if lines:
                write_commands(lines)
            self._serve_json({"status": "ok", "commands": len(lines)})
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self._serve_json({"status": "error", "message": str(e)}, code=500)

    def _handle_bulk_commands(self):
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = json.loads(body.decode("utf-8"))
            lines = []
            for cmd in data.get("commands", []):
                if cmd.get("action") == "set" and cmd.get("key"):
                    lines.append(f"set {cmd['key']} {cmd['value']}")
                elif cmd.get("action") == "action" and cmd.get("key"):
                    lines.append(f"action {cmd['key']}")
            if lines:
                write_commands(lines)
            self._serve_json({"status": "ok", "commands": len(lines)})
        except Exception as e:
            self._serve_json({"status": "error", "message": str(e)}, code=500)

    def _serve_qr(self):
        ip = get_local_ip()
        port = self.server.server_address[1]
        url = f"https://{ip}:{port}"
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=4, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            png_data = buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "max-age=3600")
            self.end_headers()
            self.wfile.write(png_data)
        except Exception as e:
            self._serve_json({"error": str(e)}, code=500)

    def _serve_main_page(self):
        ip = get_local_ip()
        port = self.server.server_address[1]
        url = f"https://{ip}:{port}"
        try:
            html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
            html = html.replace("{{SERVER_URL}}", url)
            html = html.replace("{{SERVER_IP}}", ip)
            html = html.replace("{{SERVER_PORT}}", str(port))
        except Exception:
            dlog(f"Could not load index.html, serving fallback page:\n{traceback.format_exc()}")
            html = f"<html><body><h1>Auto-Yaw Deck</h1><p>{url}</p></body></html>"
        dlog(f"Serving main page ({len(html)} bytes)")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        dlog("HTTP " + (fmt % args))

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError) as e:
            dlog(f"Connection from {self.client_address[0]} dropped mid-request: {e!r}")
        except ssl.SSLError as e:
            dlog(f"TLS error while handling request from {self.client_address[0]}: {e!r}")


# ---------------------------------------------------------------------------
# Server — surfaces TLS handshake / accept errors that socketserver normally
# swallows silently (they otherwise look like the page never loading).
# ---------------------------------------------------------------------------
class DeckHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def get_request(self):
        try:
            return super().get_request()
        except Exception as e:
            dlog(f"Connection/handshake FAILED before request: {e!r}")
            raise

    def handle_error(self, request, client_address):
        dlog(f"Unhandled error while serving {client_address}:\n{traceback.format_exc()}")


# ---------------------------------------------------------------------------
# State watcher thread
# ---------------------------------------------------------------------------
def state_watcher(interval=0.1):
    while True:
        refresh_state()
        time.sleep(interval)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Auto-Yaw Deck HTTPS Server")
    parser.add_argument("--port", type=int, default=8443, help="Port (default: 8443)")
    parser.add_argument("--cert-dir", default=str(CERT_DIR))
    parser.add_argument("--cert-port", type=int, default=8080,
                         help="Plain-HTTP port used only to download the CA cert (default: 8080)")
    parser.add_argument("--no-cert", action="store_true", help="HTTP only, no SSL")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    ip = get_local_ip()
    all_ips = get_all_local_ips()
    port = args.port

    print("=" * 60)
    print("  AUTO-YAW DECK — X-Plane Remote Control")
    print("=" * 60)

    threading.Thread(target=state_watcher, daemon=True).start()

    cert_url = None
    if args.no_cert:
        server = DeckHTTPServer(("0.0.0.0", port), DeckHTTPHandler)
        scheme = "http"
    else:
        cert_file, key_file = generate_self_signed_cert(args.cert_dir)
        if not cert_file or not key_file:
            print("\n  Use --no-cert for HTTP-only mode")
            sys.exit(1)

        server = DeckHTTPServer(("0.0.0.0", port), DeckHTTPHandler)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert_file, key_file)
        dlog(f"TLS context ready (cert={cert_file}, key={key_file})")
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        scheme = "https"

        start_cert_download_server(cert_file, args.cert_port)
        cert_url = f"http://{ip}:{args.cert_port}/cert"

    url = f"{scheme}://{ip}:{port}"
    print()
    print(f"  Server running on: {url}")
    print(f"  Local:             {scheme}://127.0.0.1:{port}")
    if len(all_ips) > 1:
        print()
        print(f"  This PC has multiple network adapters. If the phone can't reach")
        print(f"  {ip}, it may be on a different network — try one of these instead:")
        for other_ip in all_ips:
            if other_ip != ip:
                print(f"    {scheme}://{other_ip}:{port}")
    if cert_url:
        print()
        print(f"  If your phone blocks the self-signed certificate with no way to")
        print(f"  bypass it (common on Samsung), first install the CA cert from:")
        print(f"  {cert_url}")
        print(f"  (plain HTTP download, then Settings > Security > Install certificate)")
    print()
    print(f"  Open this URL on your phone:")
    print(f"  +-------------------------------------+")
    print(f"  |  {url:<37s}|")
    print(f"  +-------------------------------------+")
    print()

    # Generate QR code in terminal
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                            box_size=1, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except Exception:
        print("  (QR code unavailable - install 'qrcode' with: pip install qrcode[pil]")

    print()
    print(f"  State file:   {STATE_FILE}")
    print(f"  Commands file: {COMMANDS_FILE}")
    print()
    print("  Press Ctrl+C to stop.")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Auto-Yaw Deck] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()

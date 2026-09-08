#!/usr/bin/env python3
"""
Auto-Yaw Deck — Local HTTPS server for X-Plane remote control.
Bridges the FlyWithLua auto_yaw script to a mobile web interface.

Usage:
    python server.py [--port 8443] [--cert-dir certs]

The heavy lifting lives in the deck_* modules (paths, logging, prefs, state,
cert, http). This file keeps only the server bootstrap + orchestration and
re-exports the public names so `import server as srv` keeps working
(panel.py relies on srv.DeckHTTPServer, srv.get_local_ip(), ...).
"""

import argparse
import http.server
import os
import ssl
import subprocess
import sys
import threading
import time
import traceback

# ---------------------------------------------------------------------------
# Auto-install required packages
# ---------------------------------------------------------------------------
REQUIRED_PACKAGES = {
    'cryptography': 'cryptography',
    'qrcode': 'qrcode[pil]',
}

def _pip_available():
    """Check whether the pip module can be invoked at all."""
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=10
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False

def _pip_install(packages, verbose=False):
    """Run pip install and return (success, output)."""
    cmd = [sys.executable, '-m', 'pip', 'install', '--quiet'] + packages
    io = subprocess.PIPE if not verbose else None
    try:
        subprocess.check_call(cmd, stdout=io, stderr=io, timeout=120)
        return True, ''
    except subprocess.CalledProcessError as e:
        out = e.output or ''
        if isinstance(out, bytes):
            out = out.decode('utf-8', errors='replace')
        return False, out
    except FileNotFoundError:
        return False, 'pip not found'
    except subprocess.TimeoutExpired:
        return False, 'pip install timed out after 120s'
    except OSError as exc:
        return False, str(exc)

def ensure_packages():
    """Install missing Python packages automatically."""
    missing = []
    for module, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        return

    print(f"[Yaw Rescue] Installing missing packages: {', '.join(missing)}")

    if not _pip_available():
        print("[Yaw Rescue] pip is not available on this Python installation.")
        print("  Try: " + sys.executable + " -m ensurepip --upgrade")
        print("  Then: " + sys.executable + " -m pip install " + ' '.join(missing))
        return

    ok, output = _pip_install(missing, verbose=bool(os.environ.get('AYD_VERBOSE')))
    if ok:
        print("[Yaw Rescue] Packages installed successfully.")
        return

    # First attempt failed — show diagnostics, then one retry with verbose output
    print("[Yaw Rescue] First install attempt failed.")
    if output:
        for line in output.strip().splitlines()[-8:]:
            print("  | " + line)

    print("[Yaw Rescue] Retrying with verbose output...")
    ok2, output2 = _pip_install(missing, verbose=True)
    if ok2:
        print("[Yaw Rescue] Packages installed successfully on retry.")
        return

    if output2:
        print("[Yaw Rescue] pip output:")
        for line in output2.strip().splitlines()[-15:]:
            print("  | " + line)
    else:
        print("[Yaw Rescue] pip produced no output.")

    print("[Yaw Rescue] WARNING: Could not install required packages.")
    print("  Manual install: " + sys.executable + " -m pip install " + ' '.join(missing))
    print("  If behind a proxy, set HTTP_PROXY / HTTPS_PROXY before running.")
    print("  If offline, install packages on another machine and copy the site-packages folder.")


ensure_packages()

# ---------------------------------------------------------------------------
# Public API — re-exported from the deck_* modules so existing callers
# (panel.py and any script doing `import server as srv`) keep working.
# ---------------------------------------------------------------------------
from deck.paths import SCRIPT_DIR, STATIC_DIR, DATA_DIR, CERT_DIR, \
    STATE_FILE, COMMANDS_FILE, PREFS_FILE  # noqa: E402
from deck.log import DEBUG_LOGGING, dlog, set_debug  # noqa: E402
from deck.prefs import load_prefs, save_prefs  # noqa: E402
from deck.state import (  # noqa: E402
    DEFAULT_STATE, state_cache, state_lock,
    read_state_file, get_cached_state, refresh_state, get_xplane_state,
    write_commands,
)
from deck.cert import (  # noqa: E402
    CertHTTPHandler, start_cert_download_server,
    get_local_ip, get_all_local_ips, generate_self_signed_cert,
)
from deck.http import DeckHTTPHandler  # noqa: E402


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
    parser = argparse.ArgumentParser(description="Yaw Rescue HTTPS Server")
    parser.add_argument("--port", type=int, default=8443, help="Port (default: 8443)")
    parser.add_argument("--cert-dir", default=str(CERT_DIR))
    parser.add_argument("--cert-port", type=int, default=8080,
                         help="Plain-HTTP port used only to download the CA cert (default: 8080)")
    parser.add_argument("--no-cert", action="store_true", help="HTTP only, no SSL")
    parser.add_argument("--debug", action="store_true",
                         help="Enable debug logging (also: YAW_RESCUE_DEBUG=1)")
    args = parser.parse_args()

    if args.debug:
        set_debug(True)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    ip = get_local_ip()
    all_ips = get_all_local_ips()
    port = args.port

    print("=" * 60)
    print("  YAW RESCUE - X-Plane Remote Control")
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
        print("\n[Yaw Rescue] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()

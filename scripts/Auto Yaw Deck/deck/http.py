"""HTTP request handler for the Yaw Rescue deck (étape P1.6).

Serves static files, the main page and the JSON API. Kept free of any
server orchestration so it can be reused by both server.py and panel.py.
"""
import http.server
import io
import json
import os
import platform
import socket
import ssl
import subprocess
import traceback
from urllib.parse import urlparse

from deck.cert import get_local_ip
from deck.flight import _read_last_aircraft, find_last_airport
from deck.installer import get_install_status
from deck.log import dlog
from deck.paths import DATA_DIR, STATIC_DIR
from deck.prefs import load_prefs, save_prefs
from deck.state import get_cached_state, refresh_state, write_commands


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
            elif path == "/api/prefs":
                self._serve_json(load_prefs())
            elif path == "/api/health":
                self._serve_json({"status": "ok"})
            elif path == "/api/install-status":
                self._handle_install_status()
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
            elif path == "/api/prefs":
                self._handle_prefs()
            elif path == "/api/launch-xplane":
                self._handle_launch_xplane()
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

    def _handle_prefs(self):
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = json.loads(body.decode("utf-8"))
            lang = data.get("lang")
            if lang not in ("fr", "en"):
                self._serve_json({"status": "error", "message": "Invalid lang"}, code=400)
                return
            save_prefs({"lang": lang})
            self._serve_json({"status": "ok", "lang": lang})
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self._serve_json({"status": "error", "message": str(e)}, code=500)

    def _handle_launch_xplane(self):
        """Launch X-Plane from the web UI, optionally resuming at the last airport."""
        try:
            prefs = load_prefs()
            xplane_dir = prefs.get("xplane_path")
            if not xplane_dir or not os.path.isdir(xplane_dir):
                self._serve_json({"status": "error", "message": "X-Plane directory not configured"}, code=400)
                return
            exe_names = ["X-Plane.exe", "X-Plane-xp11.exe"]
            exe_path = None
            for exe in exe_names:
                candidate = os.path.join(xplane_dir, exe)
                if os.path.isfile(candidate):
                    exe_path = candidate
                    break
            if not exe_path:
                self._serve_json({"status": "error", "message": f"X-Plane executable not found in {xplane_dir}"}, code=400)
                return

            # Build launch args — same resume logic as the Tkinter panel
            args = [exe_path]
            try:
                icao, runway = find_last_airport(xplane_dir)
                if icao:
                    flight = {"runway_start": {"airport_id": icao}}
                    if runway:
                        flight["runway_start"]["runway"] = runway
                    aircraft = _read_last_aircraft(xplane_dir)
                    if aircraft:
                        flight["aircraft"] = {"path": aircraft}
                    flight_file = DATA_DIR / "flight.json"
                    DATA_DIR.mkdir(parents=True, exist_ok=True)
                    flight_file.write_text(json.dumps(flight, indent=2), encoding="utf-8")
                    args.append(f"--new_flight_json={flight_file}")
                    dlog(f"Resume flight: {icao} rwy={runway}")
            except Exception as e:
                dlog(f"Airport detection skipped: {e}")

            subprocess.Popen(args, cwd=xplane_dir)
            dlog(f"X-Plane launched from web: {exe_path}")
            self._serve_json({"status": "ok", "path": exe_path})
        except Exception as e:
            dlog(f"Error launching X-Plane: {e}")
            self._serve_json({"status": "error", "message": str(e)}, code=500)

    def _handle_install_status(self):
        """Return the installation status of FlyWithLua and Auto Yaw Deck."""
        try:
            prefs = load_prefs()
            xplane_dir = prefs.get("xplane_path")
            if not xplane_dir or not os.path.isdir(xplane_dir):
                self._serve_json({"status": "error", "message": "X-Plane directory not configured"}, code=400)
                return
            try:
                install_status = get_install_status(xplane_dir)
                self._serve_json({"status": "ok", "install": install_status})
            except ImportError:
                self._serve_json({"status": "error", "message": "Installation module not available"}, code=500)
        except Exception as e:
            dlog(f"Error checking install status: {e}")
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
            html = f"<html><body><h1>Yaw Rescue</h1><p>{url}</p></body></html>"
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

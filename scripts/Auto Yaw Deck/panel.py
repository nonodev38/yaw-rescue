#!/usr/bin/env python3
"""
Auto-Yaw Deck — GUI Control Panel
Starts the HTTPS server in a background thread and provides a clean
control panel with X-Plane detection, QR code, and server management.

Usage:
    python panel.py [--port 8443]
"""

import argparse
import json
import os
import re
import signal
import ssl
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# ---------------------------------------------------------------------------
# X-Plane detection
# ---------------------------------------------------------------------------

XPLANE_PROCESS_NAMES = ["X-Plane.exe", "X-Plane-xp11.exe", "X-Plane.exe"]
XPLANE_COMMON_PATHS = [
    r"D:\Jeux\X-Plane 12",
    r"C:\X-Plane 12",
    r"D:\X-Plane 12",
    r"E:\X-Plane 12",
    r"C:\Program Files\X-Plane 12",
    r"D:\Games\X-Plane 12",
    r"C:\Games\X-Plane 12",
    r"D:\Simulateurs\X-Plane 12",
    r"C:\Simulateurs\X-Plane 12",
    os.path.expanduser(r"~\X-Plane 12"),
]

XPLANE_EXE_NAMES = ["X-Plane.exe", "X-Plane-xp11.exe"]


def is_xplane_running():
    """Check if X-Plane process is running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq X-Plane.exe"],
            capture_output=True, text=True, timeout=5
        )
        if "X-Plane.exe" in result.stdout:
            return True
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq X-Plane-xp11.exe"],
            capture_output=True, text=True, timeout=5
        )
        return "X-Plane-xp11.exe" in result.stdout
    except Exception:
        return False


def find_xplane_exe():
    """Try to find X-Plane executable on the system."""
    # Check common paths
    for base in XPLANE_COMMON_PATHS:
        for exe in XPLANE_EXE_NAMES:
            path = os.path.join(base, exe)
            if os.path.isfile(path):
                return path
        # Check if it's a folder with the exe inside
        if os.path.isdir(base):
            for exe in XPLANE_EXE_NAMES:
                path = os.path.join(base, exe)
                if os.path.isfile(path):
                    return path

    # Search from the detected X-Plane directory in the project path
    # The project is inside X-Plane's FlyWithLua Scripts folder
    script_dir = Path(__file__).resolve().parent
    # Walk up to find X-Plane root
    current = script_dir
    for _ in range(10):
        for exe in XPLANE_EXE_NAMES:
            if (current / exe).is_file():
                return str(current / exe)
        current = current.parent
        if current == current.parent:
            break
    return None


def find_last_airport(xplane_root):
    """Find the last airport X-Plane started at.

    Sources, in order of reliability:
      1. Output/preferences/Freeflight.prf  — written by X-Plane itself
         (_last_start JSON block, fallback _airport key)
      2. log.txt  — last "I/FLT: Init ... apt:XXXX rwy:XX" line

    Returns (icao, runway) or (None, None).
    """
    if not xplane_root:
        return None, None
    root = Path(xplane_root)

    # 1) Freeflight.prf — the authoritative "last flight" data
    prf = root / "Output" / "preferences" / "Freeflight.prf"
    if prf.is_file():
        icao, runway = _parse_freeflight_prf(prf)
        if icao:
            return icao, runway

    # 2) log.txt — parse the last flight-init line that names an airport
    log = root / "log.txt"
    if log.is_file():
        icao, runway = _parse_log_txt(log)
        if icao:
            return icao, runway

    return None, None


def _parse_freeflight_prf(prf_path):
    """Extract (icao, runway) from Freeflight.prf.

    The file holds lines like:
        _last_start {"runway_start":{"airport_id":"LFMN","runway":"22R"}}
        _airport LFMN
    """
    icao = runway = None
    try:
        text = prf_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None, None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("_last_start "):
            try:
                start = json.loads(line[len("_last_start "):])
                if isinstance(start, dict):
                    for block in start.values():
                        if isinstance(block, dict):
                            icao = block.get("airport_id") or icao
                            runway = block.get("runway") or block.get("ramp") or runway
            except Exception:
                pass
        elif not icao and line.startswith("_airport "):
            val = line[len("_airport "):].strip()
            if val and re.fullmatch(r"[A-Z0-9]{1,5}", val):
                icao = val
    return (icao, runway) if icao else (None, None)


def _parse_log_txt(log_path):
    """Extract (icao, runway) from the last flight-init line in log.txt.

    X-Plane writes lines like:
        I/FLT: Init dat_p0 type:'runway_start' apt:LFMN rwy:22R ...
    """
    icao = runway = None
    try:
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"I/FLT: Init dat_p0 type:'[a-z_]+' apt:([A-Z0-9]+)(?:\s+rwy:(\S+))?", line)
            if m:
                icao = m.group(1)
                runway = m.group(2)
    except Exception:
        return None, None
    return (icao, runway) if icao else (None, None)


def _read_last_aircraft(xplane_root):
    """Read the last aircraft path from Freeflight.prf (_aircraft key)."""
    if not xplane_root:
        return None
    prf = Path(xplane_root) / "Output" / "preferences" / "Freeflight.prf"
    try:
        for line in prf.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("_aircraft ") and ".acf" in line:
                return line[len("_aircraft "):].strip()
    except Exception:
        pass
    return None


def start_xplane(exe_path, airport=None, runway=None):
    """Start X-Plane process, optionally resuming at the last airport.

    X-Plane 12.4+ accepts --new_flight_json=<file> where the file describes
    the starting location (same schema X-Plane itself writes into
    Freeflight.prf's _last_start).
    """
    try:
        args = [exe_path]
        if airport:
            flight = {"runway_start": {"airport_id": airport}}
            if runway:
                flight["runway_start"]["runway"] = runway
            # Reuse the last aircraft (if known) so the sim resumes the session
            aircraft = _read_last_aircraft(str(Path(exe_path).parent))
            if aircraft:
                flight["aircraft"] = {"path": aircraft}
            flight_file = Path(__file__).resolve().parent / "data" / "flight.json"
            flight_file.parent.mkdir(parents=True, exist_ok=True)
            flight_file.write_text(json.dumps(flight, indent=2), encoding="utf-8")
            args.append(f"--new_flight_json={flight_file}")
        subprocess.Popen(args, cwd=str(Path(exe_path).parent))
        return True
    except Exception as e:
        print(f"Failed to start X-Plane: {e}")
        return False


# ---------------------------------------------------------------------------
# Server runner (background thread)
# ---------------------------------------------------------------------------

server_instance = None
server_thread = None
server_started = False
server_error = None


def run_server(port, no_cert, cert_port):
    """Run the HTTPS server in a background thread."""
    global server_instance, server_started, server_error
    try:
        # Import and run server components
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import server as srv

        srv.DATA_DIR.mkdir(parents=True, exist_ok=True)
        srv.STATIC_DIR.mkdir(parents=True, exist_ok=True)

        ip = srv.get_local_ip()

        if no_cert:
            srv_instance = srv.DeckHTTPServer(("0.0.0.0", port), srv.DeckHTTPHandler)
            scheme = "http"
        else:
            cert_file, key_file = srv.generate_self_signed_cert(str(srv.CERT_DIR))
            if not cert_file or not key_file:
                server_error = "No certificate available. Use --no-cert."
                return

            srv_instance = srv.DeckHTTPServer(("0.0.0.0", port), srv.DeckHTTPHandler)
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(cert_file, key_file)
            srv_instance.socket = ctx.wrap_socket(srv_instance.socket, server_side=True)
            scheme = "https"

            srv.start_cert_download_server(cert_file, cert_port)

        # Start state watcher
        threading.Thread(target=srv.state_watcher, daemon=True).start()

        server_instance = srv_instance
        server_started = True
        srv_instance.serve_forever()

    except Exception as e:
        server_error = str(e)
        server_started = False


# ---------------------------------------------------------------------------
# GUI Panel
# ---------------------------------------------------------------------------

class AutoYawPanel:
    BG = "#0f1520"
    BG_CARD = "#1a2236"
    BORDER = "#2a3a5c"
    TEXT = "#e2e8f0"
    TEXT_DIM = "#94a3b8"
    TEXT_MUTED = "#64748b"
    ACCENT = "#3b82f6"
    SUCCESS = "#22c55e"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"

    def __init__(self, root, port, no_cert, cert_port):
        self.root = root
        self.port = port
        self.no_cert = no_cert
        self.cert_port = cert_port
        self.qr_photo = None
        self.xplane_running = False
        self.xplane_path = None
        self.server_url = ""
        self.running = True
        self.last_airport = None
        self.last_runway = None
        self.resume_at_airport = tk.BooleanVar(value=True)

        self._setup_window()
        self._build_ui()
        self._start_server_thread()
        self._start_monitoring()

    def _setup_window(self):
        self.root.title("Yaw Rescue - Control Panel")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        # Center window
        w, h = 420, 680
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill=tk.X, padx=16, pady=(16, 8))

        tk.Label(
            title_frame, text="✈ Yaw Rescue",
            font=("Segoe UI", 16, "bold"), fg=self.ACCENT, bg=self.BG
        ).pack(side=tk.LEFT)

        # Status badge
        self.status_label = tk.Label(
            title_frame, text="DÉMARRAGE...",
            font=("Segoe UI", 8, "bold"), fg=self.WARNING, bg=self.BG
        )
        self.status_label.pack(side=tk.RIGHT)

        # --- Server Info Card ---
        card1 = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card1.pack(fill=tk.X, padx=16, pady=(0, 8))

        tk.Label(
            card1, text="📡  Serveur",
            font=("Segoe UI", 9, "bold"), fg=self.TEXT_DIM, bg=self.BG_CARD,
            anchor="w"
        ).pack(fill=tk.X, padx=12, pady=(8, 4))

        self.url_label = tk.Label(
            card1, text="En attente...",
            font=("Cascadia Code", 10), fg=self.ACCENT, bg=self.BG_CARD,
            anchor="w"
        )
        self.url_label.pack(fill=tk.X, padx=12, pady=(0, 4))

        self.port_label = tk.Label(
            card1, text=f"Port: {self.port}  |  Mode: {'HTTP' if self.no_cert else 'HTTPS'}",
            font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w"
        )
        self.port_label.pack(fill=tk.X, padx=12, pady=(0, 8))

        # --- X-Plane Status Card ---
        card2 = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card2.pack(fill=tk.X, padx=16, pady=(0, 8))

        tk.Label(
            card2, text="🎮  X-Plane",
            font=("Segoe UI", 9, "bold"), fg=self.TEXT_DIM, bg=self.BG_CARD,
            anchor="w"
        ).pack(fill=tk.X, padx=12, pady=(8, 4))

        self.xplane_status_label = tk.Label(
            card2, text="Détection en cours...",
            font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w"
        )
        self.xplane_status_label.pack(fill=tk.X, padx=12)

        self.airport_label = tk.Label(
            card2, text="🛫 Dernier aéroport : détection...",
            font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w"
        )
        self.airport_label.pack(fill=tk.X, padx=12)

        self.resume_check = tk.Checkbutton(
            card2, text="Reprendre au dernier aéroport",
            variable=self.resume_at_airport,
            font=("Segoe UI", 8), fg=self.TEXT_DIM, bg=self.BG_CARD,
            activebackground=self.BG_CARD, activeforeground=self.TEXT_DIM,
            selectcolor=self.BG_CARD, highlightthickness=0, bd=0, anchor="w",
            cursor="hand2"
        )
        self.resume_check.pack(fill=tk.X, padx=12, pady=(0, 4))

        self.xplane_btn = tk.Button(
            card2, text="▶  Démarrer X-Plane",
            font=("Segoe UI", 9, "bold"), fg="white", bg=self.ACCENT,
            activebackground="#2563eb", activeforeground="white",
            relief=tk.FLAT, cursor="hand2",
            command=self._start_xplane,
            state=tk.DISABLED
        )
        self.xplane_btn.pack(fill=tk.X, padx=12, pady=(8, 8))

        # --- QR Code Card ---
        card3 = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card3.pack(fill=tk.X, padx=16, pady=(0, 8))

        tk.Label(
            card3, text="📱  QR Code",
            font=("Segoe UI", 9, "bold"), fg=self.TEXT_DIM, bg=self.BG_CARD,
            anchor="w"
        ).pack(fill=tk.X, padx=12, pady=(8, 4))

        self.qr_label = tk.Label(
            card3, text="En attente du serveur...",
            font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.BG_CARD
        )
        self.qr_label.pack(padx=12, pady=(0, 8))

        # --- Action Buttons ---
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(fill=tk.X, padx=16, pady=(8, 16))

        self.close_btn = tk.Button(
            btn_frame, text="⏹  Fermer le serveur",
            font=("Segoe UI", 10, "bold"), fg="white", bg=self.DANGER,
            activebackground="#dc2626", activeforeground="white",
            relief=tk.FLAT, cursor="hand2", height=2,
            command=self._on_close
        )
        self.close_btn.pack(fill=tk.X)

    def _start_server_thread(self):
        global server_thread
        server_thread = threading.Thread(
            target=run_server,
            args=(self.port, self.no_cert, self.cert_port),
            daemon=True
        )
        server_thread.start()

    def _start_monitoring(self):
        """Periodically check server status and X-Plane."""
        self._check_server()
        self._check_xplane()

    def _check_server(self):
        global server_started, server_error
        if server_error:
            self.status_label.config(text="ERREUR", fg=self.DANGER)
            self.url_label.config(text=server_error)
            return

        if server_started:
            from server import get_local_ip
            ip = get_local_ip()
            scheme = "http" if self.no_cert else "https"
            self.server_url = f"{scheme}://{ip}:{self.port}"
            self.status_label.config(text="EN LIGNE", fg=self.SUCCESS)
            self.url_label.config(text=self.server_url)
            self._generate_qr()
        else:
            self.status_label.config(text="DÉMARRAGE...", fg=self.WARNING)
            self.url_label.config(text="En attente...")

        self.root.after(1000, self._check_server)

    def _check_xplane(self):
        self.xplane_running = is_xplane_running()

        if self.xplane_running:
            self.xplane_status_label.config(text="✅  X-Plane en cours d'exécution", fg=self.SUCCESS)
            self.xplane_btn.config(state=tk.DISABLED)
        else:
            self.xplane_path = find_xplane_exe()
            if self.xplane_path:
                self.xplane_status_label.config(text="⚠️  X-Plane non détecté", fg=self.WARNING)
                self.xplane_btn.config(state=tk.NORMAL)
                # Detect the last airport used by X-Plane (Freeflight.prf, then log.txt)
                icao, rwy = find_last_airport(str(Path(self.xplane_path).parent))
                self.last_airport, self.last_runway = icao, rwy
                if icao:
                    label = f"🛫 Dernier aéroport : {icao}"
                    if rwy:
                        label += f" (Piste {rwy})"
                    self.airport_label.config(text=label, fg=self.TEXT_DIM)
                else:
                    self.airport_label.config(text="🛫 Dernier aéroport : inconnu", fg=self.TEXT_MUTED)
            else:
                self.xplane_status_label.config(text="❌  X-Plane introuvable sur cette machine", fg=self.DANGER)
                self.xplane_btn.config(state=tk.DISABLED)
                self.airport_label.config(text="")

        self.root.after(3000, self._check_xplane)

    def _generate_qr(self):
        """Generate and display QR code in the panel."""
        try:
            import qrcode
            from PIL import ImageTk

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=4, border=2
            )
            qr.add_data(self.server_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Resize for display
            img = img.resize((180, 180))
            self.qr_photo = ImageTk.PhotoImage(img)
            self.qr_label.config(image=self.qr_photo, text="")
        except Exception as e:
            self.qr_label.config(text=f"QR indisponible: {e}")

    def _start_xplane(self):
        if self.xplane_path:
            airport = self.last_airport if self.resume_at_airport.get() else None
            runway = self.last_runway if airport else None
            ok = start_xplane(self.xplane_path, airport, runway)
            if ok:
                if airport:
                    self.xplane_status_label.config(
                        text=f"⏳ Démarrage de X-Plane à {airport}...", fg=self.WARNING
                    )
                else:
                    self.xplane_status_label.config(text="⏳ X-Plane en cours de démarrage...", fg=self.WARNING)
                self.xplane_btn.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Erreur", f"Impossible de démarrer X-Plane:\n{self.xplane_path}")

    def _on_close(self):
        global server_instance
        self.running = False
        if server_instance:
            try:
                server_instance.shutdown()
            except Exception:
                pass
        self.root.destroy()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def minimize_console():
    """Minimize the console window on Windows."""
    if sys.platform == 'win32':
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE = 6
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Yaw Rescue Control Panel")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--cert-port", type=int, default=8080)
    parser.add_argument("--no-cert", action="store_true")
    args = parser.parse_args()

    # Ensure packages
    try:
        from server import ensure_packages
        ensure_packages()
    except Exception:
        pass

    # Need tkinter
    try:
        import tkinter
    except ImportError:
        print("[Yaw Rescue] tkinter not available. Use server.py directly.")
        print("  On Windows: install Python with tkinter (default)")
        print("  On Linux: sudo apt install python3-tk")
        sys.exit(1)

    # Minimize console window before showing GUI
    minimize_console()

    root = tk.Tk()
    panel = AutoYawPanel(root, args.port, args.no_cert, args.cert_port)
    root.mainloop()


if __name__ == "__main__":
    main()

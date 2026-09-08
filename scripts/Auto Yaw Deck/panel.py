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
import string
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox
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
    r"F:\X-Plane 12",
    r"C:\Program Files\X-Plane 12",
    r"C:\Program Files (x86)\X-Plane 12",
    r"D:\Games\X-Plane 12",
    r"C:\Games\X-Plane 12",
    r"D:\Simulateurs\X-Plane 12",
    r"C:\Simulateurs\X-Plane 12",
    r"D:\Jeux\X-Plane",
    r"C:\X-Plane",
    r"D:\X-Plane",
    r"E:\X-Plane",
    r"F:\X-Plane",
    r"D:\Games\X-Plane",
    r"C:\Games\X-Plane",
    os.path.expanduser(r"~\X-Plane 12"),
    os.path.expanduser(r"~\X-Plane"),
    os.path.expanduser(r"~\Documents\X-Plane 12"),
]

XPLANE_EXE_NAMES = ["X-Plane.exe", "X-Plane-xp11.exe"]

# Regex to match X-Plane directory names (X-Plane, X-Plane 12, X-Plane 11, etc.)
_XPLANE_DIR_RE = re.compile(r"^X-Plane(?:[\s-]+\d+)?$", re.IGNORECASE)

# Cached deep search result so we only scan drives once
_deep_search_cache = None


def _load_saved_xplane_path():
    """Load saved X-Plane path from prefs.json."""
    prefs_path = Path(__file__).resolve().parent / "data" / "prefs.json"
    try:
        if prefs_path.is_file():
            prefs = json.loads(prefs_path.read_text(encoding="utf-8"))
            saved = prefs.get("xplane_path")
            if saved and os.path.isdir(saved):
                return saved
    except Exception:
        pass
    return None


def _save_xplane_path(path):
    """Save X-Plane directory path to prefs.json."""
    prefs_path = Path(__file__).resolve().parent / "data" / "prefs.json"
    try:
        prefs = {}
        if prefs_path.is_file():
            prefs = json.loads(prefs_path.read_text(encoding="utf-8"))
        prefs["xplane_path"] = path
        prefs_path.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
    except Exception:
        pass


def _get_available_drives():
    """Get list of available drive roots (Windows) or root (Linux/Mac)."""
    if sys.platform == "win32":
        drives = []
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZAB":
            drive = f"{letter}:\\"
            if os.path.isdir(drive):
                drives.append(drive)
        return drives
    return ["/"]


def _scan_drive_for_xplane(drive_root):
    """Scan a drive for X-Plane directories (top-level + common subdirs)."""
    found = []
    # Top-level scan
    try:
        for entry in os.scandir(drive_root):
            if entry.is_dir(follow_symlinks=False) and _XPLANE_DIR_RE.match(entry.name):
                found.append(entry.path)
    except (PermissionError, OSError):
        pass
    # Also check inside common parent directories
    for parent_name in ["Games", "Jeux", "Simulateurs", "Simulators", "Flight", "FlightSim"]:
        parent_path = os.path.join(drive_root, parent_name)
        if os.path.isdir(parent_path):
            try:
                for entry in os.scandir(parent_path):
                    if entry.is_dir(follow_symlinks=False) and _XPLANE_DIR_RE.match(entry.name):
                        found.append(entry.path)
            except (PermissionError, OSError):
                pass
    return found


def deep_find_xplane():
    """Deep search across all drives for X-Plane directories."""
    global _deep_search_cache
    if _deep_search_cache is not None:
        return _deep_search_cache or None

    for drive in _get_available_drives():
        candidates = _scan_drive_for_xplane(drive)
        for path in candidates:
            for exe in XPLANE_EXE_NAMES:
                if os.path.isfile(os.path.join(path, exe)):
                    _deep_search_cache = path
                    return path
        # If directory exists but no exe found yet, keep as candidate
        if candidates:
            _deep_search_cache = candidates[0]
            return candidates[0]

    _deep_search_cache = ""
    return None


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
    """Try to find X-Plane executable on the system.

    Search order:
      1. Saved path from prefs.json (user-selected or previously detected)
      2. Common hardcoded paths
      3. Walk up from the script directory (FlyWithLua Scripts)
      4. Deep scan all drives for directories named X-Plane*
    """
    # 1. Check saved path from prefs
    saved = _load_saved_xplane_path()
    if saved:
        for exe in XPLANE_EXE_NAMES:
            path = os.path.join(saved, exe)
            if os.path.isfile(path):
                return path

    # 2. Check common paths
    for base in XPLANE_COMMON_PATHS:
        if os.path.isdir(base):
            for exe in XPLANE_EXE_NAMES:
                path = os.path.join(base, exe)
                if os.path.isfile(path):
                    _save_xplane_path(base)
                    return path

    # 3. Walk up from the script directory
    script_dir = Path(__file__).resolve().parent
    current = script_dir
    for _ in range(10):
        for exe in XPLANE_EXE_NAMES:
            if (current / exe).is_file():
                _save_xplane_path(str(current))
                return str(current / exe)
        current = current.parent
        if current == current.parent:
            break

    # 4. Deep scan all drives
    deep = deep_find_xplane()
    if deep:
        for exe in XPLANE_EXE_NAMES:
            path = os.path.join(deep, exe)
            if os.path.isfile(path):
                _save_xplane_path(deep)
                return path

    return None


# ---------------------------------------------------------------------------
# Installation helpers
# ---------------------------------------------------------------------------

FLYWITHLUA_URL = "https://github.com/X-FriX/FlyWithLua/releases/download/latest/FlyWithLua_NXT.zip"


def _find_flywithlua_dir(xplane_root):
    """Find the FlyWithLua plugin directory in X-Plane."""
    if not xplane_root:
        return None
    root = Path(xplane_root)
    plugins_dir = root / "Resources" / "plugins"
    if not plugins_dir.is_dir():
        return None
    for d in plugins_dir.iterdir():
        if d.is_dir():
            name_lower = d.name.lower()
            if "flywithlua" in name_lower or "fly_with_lua" in name_lower:
                return d
    return None


def _is_flywithlua_installed(xplane_root):
    """Check if FlyWithLua is installed."""
    fl_dir = _find_flywithlua_dir(xplane_root)
    return (True, fl_dir) if fl_dir else (False, None)


def _get_scripts_dir(xplane_root):
    """Get the Scripts directory inside FlyWithLua. Creates it if missing."""
    fl_dir = _find_flywithlua_dir(xplane_root)
    if not fl_dir:
        return None
    scripts = fl_dir / "Scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    return scripts


def install_flywithlua(xplane_root):
    """Download and install FlyWithLua NXT into X-Plane."""
    import urllib.request
    import zipfile
    import tempfile

    root = Path(xplane_root)
    plugins_dir = root / "Resources" / "plugins"
    if not plugins_dir.is_dir():
        return False, "Plugins directory not found"
    try:
        tmp_dir = Path(tempfile.mkdtemp())
        zip_path = tmp_dir / "FlyWithLua_NXT.zip"
        urllib.request.urlretrieve(FLYWITHLUA_URL, str(zip_path))
        with zipfile.ZipFile(str(zip_path), 'r') as zf:
            zf.extractall(str(plugins_dir))
        zip_path.unlink(missing_ok=True)
        tmp_dir.rmdir(ignore_errors=True)
        return True, "FlyWithLua NXT installed successfully"
    except Exception as e:
        return False, f"Installation failed: {e}"


def install_auto_yaw_deck(xplane_root):
    """Install Auto Yaw Deck files into FlyWithLua/Scripts.

    IMPORTANT: If the script is already running from the destination directory,
    we skip the folder copy to avoid deleting ourselves. Only the Lua files
    are copied/updated in that case.
    """
    import shutil

    root = Path(xplane_root)
    scripts_dir = _get_scripts_dir(xplane_root)
    if not scripts_dir:
        return False, "FlyWithLua Scripts directory not found"

    src_dir = Path(__file__).resolve().parent
    running_in_place = (src_dir == scripts_dir / "Auto Yaw Deck")

    try:
        # 1. Copy Auto Yaw Deck folder (skip if running from destination)
        dst_deck = scripts_dir / "Auto Yaw Deck"
        if not running_in_place:
            if dst_deck.exists():
                shutil.rmtree(str(dst_deck))
            shutil.copytree(str(src_dir), str(dst_deck))

        # 2. Copy auto_yaw_deck.lua to Scripts/
        src_bridge = src_dir / ".." / ".." / "auto_yaw_deck.lua"
        if not src_bridge.is_file():
            src_bridge = src_dir.parent / "auto_yaw_deck.lua"
        if src_bridge.is_file():
            shutil.copy2(str(src_bridge), str(scripts_dir / "auto_yaw_deck.lua"))

        # 3. Copy auto_yaw.lua to Scripts/
        src_yaw = src_dir.parent / "auto_yaw.lua"
        if src_yaw.is_file():
            shutil.copy2(str(src_yaw), str(scripts_dir / "auto_yaw.lua"))

        # 4. Cleanup: remove certs directory from installed copy
        if dst_deck.exists():
            dst_certs = dst_deck / "certs"
            if dst_certs.exists():
                shutil.rmtree(str(dst_certs))

        # 5. Cleanup: remove AutoYaw_profiles.cfg backup if present
        for cfg_name in ["AutoYaw_profiles.cfg", "AutoYaw_profiles.cfg.bak"]:
            cfg_file = scripts_dir / cfg_name
            if cfg_file.is_file():
                cfg_file.unlink()
        dst_cfg = dst_deck / "AutoYaw_profiles.cfg"
        if dst_cfg.is_file():
            dst_cfg.unlink()

        return True, f"Auto Yaw Deck installed to {scripts_dir}"
    except Exception as e:
        return False, f"Installation failed: {e}"


def get_install_status(xplane_root):
    """Check the installation status of FlyWithLua and Auto Yaw Deck."""
    status = {
        "flywithlua": False, "flywithlua_dir": None,
        "auto_yaw_deck": False, "auto_yaw_lua": False, "auto_yaw_deck_lua": False,
    }
    fl_installed, fl_dir = _is_flywithlua_installed(xplane_root)
    status["flywithlua"] = fl_installed
    status["flywithlua_dir"] = str(fl_dir) if fl_dir else None
    if fl_dir:
        scripts = fl_dir / "Scripts"
        status["auto_yaw_deck"] = (scripts / "Auto Yaw Deck").is_dir()
        status["auto_yaw_lua"] = (scripts / "auto_yaw.lua").is_file()
        status["auto_yaw_deck_lua"] = (scripts / "auto_yaw_deck.lua").is_file()
    return status


# ---------------------------------------------------------------------------
# PID file — instance management
# ---------------------------------------------------------------------------
PID_FILE = Path(__file__).resolve().parent / "data" / "panel.pid"


def _kill_previous_instances():
    """Detect and kill any previous instances of panel.py before starting."""
    my_pid = os.getpid()
    killed = 0
    # Strategy 1: PID file
    if PID_FILE.is_file():
        try:
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            if old_pid != my_pid:
                _kill_pid(old_pid)
                killed += 1
        except Exception:
            pass
    # Strategy 2: tasklist scan (Windows)
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                parts = line.strip().strip('"').split('","')
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1])
                        if pid != my_pid:
                            cmd_result = subprocess.run(
                                ["wmic", "process", "where", f"ProcessId={pid}",
                                 "get", "CommandLine", "/FORMAT:list"],
                                capture_output=True, text=True, timeout=5
                            )
                            if "panel.py" in cmd_result.stdout and "Auto Yaw Deck" in cmd_result.stdout:
                                _kill_pid(pid)
                                killed += 1
                    except (ValueError, IndexError):
                        pass
        except Exception:
            pass
    else:
        try:
            result = subprocess.run(
                ["pgrep", "-f", "panel.py"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                try:
                    pid = int(line.strip())
                    if pid != my_pid:
                        _kill_pid(pid)
                        killed += 1
                except ValueError:
                    pass
        except Exception:
            pass
    if killed > 0:
        print(f"[Yaw Rescue] Closed {killed} previous instance(s).")
        time.sleep(1)
    try:
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(str(my_pid), encoding="utf-8")
    except Exception:
        pass


def _kill_pid(pid):
    """Kill a process by PID."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=5)
        else:
            os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


def _cleanup_pid_file():
    """Remove the PID file on exit."""
    try:
        if PID_FILE.is_file():
            stored = int(PID_FILE.read_text(encoding="utf-8").strip())
            if stored == os.getpid():
                PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


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
# Translations
# ---------------------------------------------------------------------------

PANEL_I18N = {
    'fr': {
        'title': 'Yaw Rescue - Panneau de contrôle',
        'status_starting': 'DÉMARRAGE...',
        'status_online': 'EN LIGNE',
        'status_error': 'ERREUR',
        'server_title': '📡  Serveur',
        'server_waiting': 'En attente...',
        'server_port_mode': 'Port: {port}  |  Mode: {mode}',
        'xplane_title': '🎮  X-Plane',
        'xplane_detecting': '🔍  Recherche de X-Plane...',
        'xplane_running': '✅  X-Plane en cours d\'exécution',
        'xplane_found_not_running': '🟢  X-Plane trouvé mais pas lancé',
        'xplane_found_path': '📂  {path}',
        'xplane_not_found': '❌  X-Plane non trouvé sur cette machine',
        'airport_label': '🛫 Dernier aéroport : {airport}',
        'airport_runway': ' (Piste {runway})',
        'airport_unknown': '🛫 Dernier aéroport : inconnu',
        'resume_check': 'Reprendre au dernier aéroport',
        'start_xplane': '▶  Démarrer X-Plane',
        'xplane_starting': '⏳ X-Plane en cours de démarrage...',
        'xplane_starting_at': '⏳ Démarrage de X-Plane à {airport}...',
        'qr_title': '📱  QR Code',
        'qr_waiting': 'En attente du serveur...',
        'qr_unavailable': 'QR indisponible: {error}',
        'close_btn': '⏹  Fermer le serveur',
        'url_click_hint': '[Cliquez pour ouvrir]',
        'error_title': 'Erreur',
        'error_start_xplane': 'Impossible de démarrer X-Plane:\n{path}',
        'browse_xplane': '📂  Sélectionner le répertoire X-Plane',
        'xplane_invalid_dir': 'Le répertoire sélectionné ne contient pas d\'exécutable X-Plane valide.',
        'install_title': '📦  Installation',
        'install_checking': '🔍 Vérification de l\'installation...',
        'install_ready': '✅ FlyWithLua + Auto Yaw Deck installés',
        'install_flywithlua_missing': '❌ FlyWithLua non installé —\nCliquez pour l\'installer automatiquement',
        'install_files_missing': '⚠️ FlyWithLua trouvé mais Auto Yaw Deck manquant —\nCliquez pour installer les fichiers',
        'install_btn': '📦  Installer / Mettre à jour',
        'install_btn_installing': '⏳ Installation en cours...',
        'install_success': '✅ Installation terminée avec succès !',
        'install_error': '❌ Erreur lors de l\'installation :\n{error}',
    },
    'en': {
        'title': 'Yaw Rescue - Control Panel',
        'status_starting': 'STARTING...',
        'status_online': 'ONLINE',
        'status_error': 'ERROR',
        'server_title': '📡  Server',
        'server_waiting': 'Waiting...',
        'server_port_mode': 'Port: {port}  |  Mode: {mode}',
        'xplane_title': '🎮  X-Plane',
        'xplane_detecting': '🔍  Searching for X-Plane...',
        'xplane_running': '✅  X-Plane is running',
        'xplane_found_not_running': '🟢  X-Plane found but not running',
        'xplane_found_path': '📂  {path}',
        'xplane_not_found': '❌  X-Plane not found on this machine',
        'airport_label': '🛫 Last airport: {airport}',
        'airport_runway': ' (Runway {runway})',
        'airport_unknown': '🛫 Last airport: unknown',
        'resume_check': 'Resume at last airport',
        'start_xplane': '▶  Start X-Plane',
        'xplane_starting': '⏳ Starting X-Plane...',
        'xplane_starting_at': '⏳ Starting X-Plane at {airport}...',
        'qr_title': '📱  QR Code',
        'qr_waiting': 'Waiting for server...',
        'qr_unavailable': 'QR unavailable: {error}',
        'close_btn': '⏹  Stop server',
        'url_click_hint': '[Click to open]',
        'error_title': 'Error',
        'error_start_xplane': 'Cannot start X-Plane:\n{path}',
        'browse_xplane': '📂  Select X-Plane directory',
        'xplane_invalid_dir': 'Selected directory does not contain a valid X-Plane executable.',
        'install_title': '📦  Installation',
        'install_checking': '🔍 Checking installation...',
        'install_ready': '✅ FlyWithLua + Auto Yaw Deck installed',
        'install_flywithlua_missing': '❌ FlyWithLua not installed —\nClick to install automatically',
        'install_files_missing': '⚠️ FlyWithLua found but Auto Yaw Deck missing —\nClick to install files',
        'install_btn': '📦  Install / Update',
        'install_btn_installing': '⏳ Installing...',
        'install_success': '✅ Installation completed successfully!',
        'install_error': '❌ Installation error:\n{error}',
    }
}


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
        self.current_lang = 'fr'
        self.t = PANEL_I18N[self.current_lang]

        self._setup_window()
        self._build_ui()
        self._start_server_thread()
        self._start_monitoring()

    def _setup_window(self):
        self.root.title(self.t['title'])
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        # Center window
        w, h = 420, 750
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

        # Language toggle button
        self.lang_btn = tk.Button(
            title_frame, text="EN",
            font=("Segoe UI", 9, "bold"), fg="white", bg=self.ACCENT,
            activebackground="#2563eb", activeforeground="white",
            relief=tk.FLAT, cursor="hand2", width=3,
            command=self._toggle_language
        )
        self.lang_btn.pack(side=tk.RIGHT, padx=(0, 8))

        # Status badge
        self.status_label = tk.Label(
            title_frame, text=self.t['status_starting'],
            font=("Segoe UI", 8, "bold"), fg=self.WARNING, bg=self.BG
        )
        self.status_label.pack(side=tk.RIGHT)

        # --- Server Info Card ---
        card1 = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card1.pack(fill=tk.X, padx=16, pady=(0, 8))

        self.server_title_label = tk.Label(
            card1, text=self.t['server_title'],
            font=("Segoe UI", 9, "bold"), fg=self.TEXT_DIM, bg=self.BG_CARD,
            anchor="w"
        )
        self.server_title_label.pack(fill=tk.X, padx=12, pady=(8, 4))

        self.url_label = tk.Label(
            card1, text=self.t['server_waiting'],
            font=("Cascadia Code", 10), fg=self.ACCENT, bg=self.BG_CARD,
            anchor="w", cursor="hand2", highlightthickness=0
        )
        self.url_label.pack(fill=tk.X, padx=12, pady=(0, 4))
        self.url_label.bind("<Button-1>", self._open_url)
        self.url_label.bind("<ButtonRelease-1>", lambda e: None)

        self.port_label = tk.Label(
            card1, text=self.t['server_port_mode'].format(port=self.port, mode='HTTP' if self.no_cert else 'HTTPS'),
            font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w"
        )
        self.port_label.pack(fill=tk.X, padx=12, pady=(0, 8))

        # --- X-Plane Status Card ---
        card2 = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card2.pack(fill=tk.X, padx=16, pady=(0, 8))

        self.xplane_title_label = tk.Label(
            card2, text=self.t['xplane_title'],
            font=("Segoe UI", 9, "bold"), fg=self.TEXT_DIM, bg=self.BG_CARD,
            anchor="w"
        )
        self.xplane_title_label.pack(fill=tk.X, padx=12, pady=(8, 4))

        self.xplane_status_label = tk.Label(
            card2, text=self.t['xplane_detecting'],
            font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w"
        )
        self.xplane_status_label.pack(fill=tk.X, padx=12)

        self.path_label = tk.Label(
            card2, text="",
            font=("Cascadia Code", 7), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w"
        )
        self.path_label.pack(fill=tk.X, padx=12)

        self.airport_label = tk.Label(
            card2, text=self.t['airport_label'].format(airport='...'),
            font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w"
        )
        self.airport_label.pack(fill=tk.X, padx=12)

        self.resume_check = tk.Checkbutton(
            card2, text=self.t['resume_check'],
            variable=self.resume_at_airport,
            font=("Segoe UI", 8), fg=self.TEXT_DIM, bg=self.BG_CARD,
            activebackground=self.BG_CARD, activeforeground=self.TEXT_DIM,
            selectcolor=self.BG_CARD, highlightthickness=0, bd=0, anchor="w",
            cursor="hand2"
        )
        self.resume_check.pack(fill=tk.X, padx=12, pady=(0, 4))

        self.xplane_btn = tk.Button(
            card2, text=self.t['start_xplane'],
            font=("Segoe UI", 9, "bold"), fg="white", bg=self.ACCENT,
            activebackground="#2563eb", activeforeground="white",
            relief=tk.FLAT, cursor="hand2",
            command=self._start_xplane,
            state=tk.DISABLED
        )
        self.xplane_btn.pack(fill=tk.X, padx=12, pady=(8, 4))

        self.browse_btn = tk.Button(
            card2, text=self.t['browse_xplane'],
            font=("Segoe UI", 9), fg="white", bg="#475569",
            activebackground="#64748b", activeforeground="white",
            relief=tk.FLAT, cursor="hand2",
            command=self._browse_xplane_dir
        )

        # --- Installation Card ---
        card_install = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card_install.pack(fill=tk.X, padx=16, pady=(0, 8))

        self.install_title_label = tk.Label(
            card_install, text=self.t['install_title'],
            font=("Segoe UI", 9, "bold"), fg=self.TEXT_DIM, bg=self.BG_CARD,
            anchor="w"
        )
        self.install_title_label.pack(fill=tk.X, padx=12, pady=(8, 4))

        self.install_status_label = tk.Label(
            card_install, text=self.t['install_checking'],
            font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.BG_CARD,
            anchor="w", wraplength=380, justify="left"
        )
        self.install_status_label.pack(fill=tk.X, padx=12)

        self.install_btn = tk.Button(
            card_install, text=self.t['install_btn'],
            font=("Segoe UI", 9, "bold"), fg="white", bg="#22c55e",
            activebackground="#16a34a", activeforeground="white",
            relief=tk.FLAT, cursor="hand2",
            command=self._run_install,
            state=tk.DISABLED
        )
        self.install_btn.pack(fill=tk.X, padx=12, pady=(8, 8))

        # --- QR Code Card ---
        card3 = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card3.pack(fill=tk.X, padx=16, pady=(0, 8))

        self.qr_title_label = tk.Label(
            card3, text=self.t['qr_title'],
            font=("Segoe UI", 9, "bold"), fg=self.TEXT_DIM, bg=self.BG_CARD,
            anchor="w"
        )
        self.qr_title_label.pack(fill=tk.X, padx=12, pady=(8, 4))

        self.qr_label = tk.Label(
            card3, text=self.t['qr_waiting'],
            font=("Segoe UI", 8), fg=self.TEXT_MUTED, bg=self.BG_CARD
        )
        self.qr_label.pack(padx=12, pady=(0, 8))

        # --- Action Buttons ---
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(fill=tk.X, padx=16, pady=(8, 16))

        self.close_btn = tk.Button(
            btn_frame, text=self.t['close_btn'],
            font=("Segoe UI", 10, "bold"), fg="white", bg=self.DANGER,
            activebackground="#dc2626", activeforeground="white",
            relief=tk.FLAT, cursor="hand2", height=2,
            command=self._on_close
        )
        self.close_btn.pack(fill=tk.X)

    def _toggle_language(self):
        """Switch between FR and EN."""
        self.current_lang = 'en' if self.current_lang == 'fr' else 'fr'
        self.t = PANEL_I18N[self.current_lang]
        self.lang_btn.config(text='FR' if self.current_lang == 'en' else 'EN')
        self._update_labels()

    def _update_labels(self):
        """Update all text labels with current language."""
        self.root.title(self.t['title'])
        self.status_label.config(text=self.t['status_starting'])
        self.server_title_label.config(text=self.t['server_title'])
        self.url_label.config(text=self.t['server_waiting'], cursor='hand2')
        self.url_label.bind('<Button-1>', self._open_url)
        self.port_label.config(text=self.t['server_port_mode'].format(
            port=self.port, mode='HTTP' if self.no_cert else 'HTTPS'
        ))
        self.xplane_title_label.config(text=self.t['xplane_title'])
        self.xplane_status_label.config(text=self.t['xplane_detecting'])
        self.path_label.config(text="")
        self.airport_label.config(text=self.t['airport_label'].format(airport='...'))
        self.resume_check.config(text=self.t['resume_check'])
        self.xplane_btn.config(text=self.t['start_xplane'])
        self.install_title_label.config(text=self.t['install_title'])
        self.install_btn.config(text=self.t['install_btn'])
        self.qr_title_label.config(text=self.t['qr_title'])
        self.qr_label.config(text=self.t['qr_waiting'])
        self.close_btn.config(text=self.t['close_btn'])

        if self.server_url:
            self.url_label.config(text=self.server_url, cursor='hand2')
        else:
            self.url_label.config(text=self.t['server_waiting'], cursor='hand2')

    def _update_url_label(self):
        """Update URL label appearance based on whether it's clickable."""
        if self.server_url:
            self.url_label.config(fg=self.ACCENT, cursor="hand2")
        else:
            self.url_label.config(fg=self.ACCENT, cursor="")

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

    # Cached reference to server module (set once server thread imports it)
    _srv = None

    def _check_server(self):
        global server_started, server_error, server_instance
        if server_error:
            self.status_label.config(text=self.t['status_error'], fg=self.DANGER)
            self.url_label.config(text=server_error)
            return

        if server_started and self._srv is None:
            import server as srv_mod
            self._srv = srv_mod

        if server_started and self._srv:
            ip = self._srv.get_local_ip()
            scheme = "http" if self.no_cert else "https"
            self.server_url = f"{scheme}://{ip}:{self.port}"
            self.status_label.config(text=self.t['status_online'], fg=self.SUCCESS)
            self.url_label.config(text=self.server_url)
            self._update_url_label()
            self._generate_qr()
        else:
            self.status_label.config(text=self.t['status_starting'], fg=self.WARNING)
            self.url_label.config(text=self.t['server_waiting'])

        self.root.after(1000, self._check_server)

    def _show_browse_btn(self):
        try:
            self.browse_btn.pack_info()
        except Exception:
            self.browse_btn.pack(fill=tk.X, padx=12, pady=(0, 8))

    def _hide_browse_btn(self):
        try:
            self.browse_btn.pack_forget()
        except Exception:
            pass

    def _check_xplane(self):
        self.xplane_running = is_xplane_running()

        if self.xplane_running:
            self.xplane_status_label.config(text=self.t['xplane_running'], fg=self.SUCCESS)
            self.xplane_btn.config(state=tk.DISABLED)
            self._hide_browse_btn()
            self.path_label.config(text="")
        else:
            self.xplane_path = find_xplane_exe()
            if self.xplane_path:
                xplane_dir = str(Path(self.xplane_path).parent)
                self.xplane_status_label.config(text=self.t['xplane_found_not_running'], fg=self.WARNING)
                self.path_label.config(text=self.t['xplane_found_path'].format(path=xplane_dir), fg=self.TEXT_MUTED)
                self.xplane_btn.config(state=tk.NORMAL)
                self._show_browse_btn()
                icao, rwy = find_last_airport(xplane_dir)
                self.last_airport, self.last_runway = icao, rwy
                if icao:
                    label = self.t['airport_label'].format(airport=icao)
                    if rwy:
                        label += self.t['airport_runway'].format(runway=rwy)
                    self.airport_label.config(text=label, fg=self.TEXT_DIM)
                else:
                    self.airport_label.config(text=self.t['airport_unknown'], fg=self.TEXT_MUTED)
                self._check_install()
            else:
                self.xplane_status_label.config(text=self.t['xplane_not_found'], fg=self.DANGER)
                self.path_label.config(text="")
                self.xplane_btn.config(state=tk.DISABLED)
                self._show_browse_btn()
                self.airport_label.config(text="")
                self.install_status_label.config(text="")
                self.install_btn.config(state=tk.DISABLED)

        self.root.after(3000, self._check_xplane)

    def _check_install(self):
        if not self.xplane_path:
            self.install_status_label.config(text="")
            self.install_btn.config(state=tk.DISABLED)
            return
        xplane_dir = str(Path(self.xplane_path).parent)
        status = get_install_status(xplane_dir)
        if status["flywithlua"] and status["auto_yaw_deck"] and status["auto_yaw_lua"]:
            self.install_status_label.config(text=self.t['install_ready'], fg="#22c55e")
            self.install_btn.config(state=tk.DISABLED)
        elif not status["flywithlua"]:
            self.install_status_label.config(text=self.t['install_flywithlua_missing'], fg="#ef4444")
            self.install_btn.config(state=tk.NORMAL)
        else:
            self.install_status_label.config(text=self.t['install_files_missing'], fg="#f59e0b")
            self.install_btn.config(state=tk.NORMAL)

    def _run_install(self):
        if not self.xplane_path:
            return
        xplane_dir = str(Path(self.xplane_path).parent)
        self.install_btn.config(state=tk.DISABLED, text=self.t['install_btn_installing'])
        self.install_status_label.config(text=self.t['install_btn_installing'], fg=self.ACCENT)

        def _do_install():
            try:
                status = get_install_status(xplane_dir)
                if not status["flywithlua"]:
                    self.root.after(0, lambda: self.install_status_label.config(
                        text="⏳ Téléchargement de FlyWithLua NXT...", fg=self.ACCENT))
                    ok, msg = install_flywithlua(xplane_dir)
                    if not ok:
                        self.root.after(0, lambda: self._install_done(False, msg))
                        return
                    status = get_install_status(xplane_dir)
                if not status["auto_yaw_deck"] or not status["auto_yaw_lua"]:
                    self.root.after(0, lambda: self.install_status_label.config(
                        text="⏳ Installation des fichiers Auto Yaw Deck...", fg=self.ACCENT))
                    ok, msg = install_auto_yaw_deck(xplane_dir)
                    if not ok:
                        self.root.after(0, lambda: self._install_done(False, msg))
                        return
                self.root.after(0, lambda: self._install_done(True, ""))
            except Exception as e:
                self.root.after(0, lambda: self._install_done(False, str(e)))

        threading.Thread(target=_do_install, daemon=True).start()

    def _install_done(self, success, error_msg):
        if success:
            self.install_status_label.config(text=self.t['install_success'], fg="#22c55e")
            self.install_btn.config(state=tk.DISABLED, text=self.t['install_btn'])
        else:
            self.install_status_label.config(
                text=self.t['install_error'].format(error=error_msg), fg="#ef4444")
            self.install_btn.config(state=tk.NORMAL, text=self.t['install_btn'])

    def _browse_xplane_dir(self):
        directory = filedialog.askdirectory(title=self.t['browse_xplane'], mustexist=True)
        if not directory:
            return
        found_exe = None
        for exe in XPLANE_EXE_NAMES:
            if os.path.isfile(os.path.join(directory, exe)):
                found_exe = os.path.join(directory, exe)
                break
        if found_exe:
            self.xplane_path = found_exe
            _save_xplane_path(directory)
            global _deep_search_cache
            _deep_search_cache = None
            self.xplane_status_label.config(text=self.t['xplane_found_not_running'], fg=self.WARNING)
            self.path_label.config(text=self.t['xplane_found_path'].format(path=directory), fg=self.TEXT_MUTED)
            self.xplane_btn.config(state=tk.NORMAL)
            self._show_browse_btn()
            icao, rwy = find_last_airport(directory)
            self.last_airport, self.last_runway = icao, rwy
            if icao:
                label = self.t['airport_label'].format(airport=icao)
                if rwy:
                    label += self.t['airport_runway'].format(runway=rwy)
                self.airport_label.config(text=label, fg=self.TEXT_DIM)
            else:
                self.airport_label.config(text=self.t['airport_unknown'], fg=self.TEXT_MUTED)
            self._check_install()
        else:
            messagebox.showwarning(self.t['error_title'], self.t['xplane_invalid_dir'])

        self.root.after(3000, self._check_xplane)

    def _open_url(self, event=None):
        """Open the server URL in the default web browser."""
        if self.server_url:
            try:
                webbrowser.open(self.server_url)
            except Exception as e:
                pass

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
            self.qr_label.config(text=self.t['qr_unavailable'].format(error=e))

    def _start_xplane(self):
        if self.xplane_path:
            airport = self.last_airport if self.resume_at_airport.get() else None
            runway = self.last_runway if airport else None
            ok = start_xplane(self.xplane_path, airport, runway)
            if ok:
                if airport:
                    self.xplane_status_label.config(
                        text=self.t['xplane_starting_at'].format(airport=airport), fg=self.WARNING
                    )
                else:
                    self.xplane_status_label.config(text=self.t['xplane_starting'], fg=self.WARNING)
                self.xplane_btn.config(state=tk.DISABLED)
            else:
                messagebox.showerror(self.t['error_title'], self.t['error_start_xplane'].format(path=self.xplane_path))

    def _on_close(self):
        global server_instance
        self.running = False
        _cleanup_pid_file()
        if server_instance:
            try:
                server_instance.shutdown()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass
        hide_console()
        os._exit(0)


# ---------------------------------------------------------------------------
# Main
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


def hide_console():
    """Hide the console window on Windows before exiting."""
    if sys.platform == 'win32':
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
        except Exception:
            pass


def _write_crash_log(msg):
    """Append a crash diagnostic to data/crash.log so users can report it."""
    try:
        data_dir = Path(__file__).resolve().parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        log_file = data_dir / "crash.log"
        with open(log_file, "a", encoding="utf-8") as f:
            import traceback
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
            f.write(traceback.format_exc() + "\n")
            f.write("-" * 60 + "\n")
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Yaw Rescue Control Panel")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--cert-port", type=int, default=8080)
    parser.add_argument("--no-cert", action="store_true")
    args = parser.parse_args()

    # Need tkinter
    try:
        import tkinter
    except ImportError:
        print("[Yaw Rescue] tkinter not available. Use server.py directly.")
        print("  On Windows: install Python with tkinter (default)")
        print("  On Linux: sudo apt install python3-tk")
        sys.exit(1)

    # Kill any previous instances still running
    _kill_previous_instances()

    # Minimize console window before showing GUI
    minimize_console()

    try:
        root = tk.Tk()
        panel = AutoYawPanel(root, args.port, args.no_cert, args.cert_port)
        root.mainloop()
    except Exception as e:
        _write_crash_log(f"PANEL CRASH: {e}")
        print(f"[Yaw Rescue] FATAL: {e}")
        print("  See data/crash.log for details.")
        input("Press Enter to exit...")
    finally:
        _cleanup_pid_file()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            _write_crash_log(f"MAIN CRASH: {e}")
        except Exception:
            pass
        print(f"[Yaw Rescue] FATAL: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

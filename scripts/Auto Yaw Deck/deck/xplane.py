"""X-Plane detection & executable finder (étape P2.1).

Search order used by find_xplane_exe():
  1. Saved path from prefs.json (user-selected or previously detected)
  2. Common hardcoded paths
  3. Walk up from the script directory (FlyWithLua Scripts)
  4. Deep scan all drives for directories named X-Plane*
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from deck.paths import PREFS_FILE

XPLANE_PROCESS_NAMES = ["X-Plane.exe", "X-Plane-xp11.exe"]
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


def clear_deep_search_cache():
    """Invalidate the deep-search cache (called after the user picks a folder)."""
    global _deep_search_cache
    _deep_search_cache = None


def _load_saved_xplane_path():
    """Load saved X-Plane path from prefs.json."""
    try:
        if PREFS_FILE.is_file():
            prefs = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
            saved = prefs.get("xplane_path")
            if saved and os.path.isdir(saved):
                return saved
    except Exception:
        pass
    return None


def _save_xplane_path(path):
    """Save X-Plane directory path to prefs.json."""
    try:
        prefs = {}
        if PREFS_FILE.is_file():
            prefs = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
        prefs["xplane_path"] = path
        PREFS_FILE.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
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
        for proc in XPLANE_PROCESS_NAMES:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {proc}"],
                capture_output=True, text=True, timeout=5
            )
            if proc in result.stdout:
                return True
        return False
    except Exception:
        return False


def find_xplane_exe():
    """Try to find X-Plane executable on the system (see module docstring)."""
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

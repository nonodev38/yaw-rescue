"""Shared filesystem paths for Yaw Rescue (server + panel).

Single source of truth so deck.state / deck.prefs / deck.http don't each
recompute the project layout.
"""
from pathlib import Path

# deck/paths.py -> project root = parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = SCRIPT_DIR / "static"
DATA_DIR = SCRIPT_DIR / "data"
CERT_DIR = SCRIPT_DIR / "certs"

STATE_FILE = DATA_DIR / "state.txt"
COMMANDS_FILE = DATA_DIR / "commands.txt"
PREFS_FILE = DATA_DIR / "prefs.json"

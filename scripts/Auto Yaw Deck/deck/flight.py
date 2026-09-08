"""Last-flight resume helpers and X-Plane launcher (étape P2.3).

Shared by the Tkinter panel (start_xplane) and the web API
(deck_http launches X-Plane with the same resume logic).
"""
import json
import re
import subprocess
from pathlib import Path

from deck.paths import DATA_DIR


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
            flight_file = DATA_DIR / "flight.json"
            flight_file.parent.mkdir(parents=True, exist_ok=True)
            flight_file.write_text(json.dumps(flight, indent=2), encoding="utf-8")
            args.append(f"--new_flight_json={flight_file}")
        subprocess.Popen(args, cwd=str(Path(exe_path).parent))
        return True
    except Exception as e:
        print(f"Failed to start X-Plane: {e}")
        return False

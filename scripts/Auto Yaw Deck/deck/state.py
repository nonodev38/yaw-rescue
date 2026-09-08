"""X-Plane state — reads data/state.txt, tracks the sim process/log and
provides the cached state consumed by the HTTP API (étape P1.4).
"""
import os
import subprocess
import threading
import time

from deck.paths import COMMANDS_FILE, DATA_DIR, STATE_FILE
from deck.prefs import load_prefs

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
    "rudder_trim": "0.0", "flap_ratio": "0.0", "flap_vfe": "0.0",
    "flap_alert": "false", "gear_nose": "0.0", "gear_left": "0.0",
    "gear_right": "0.0", "rpm": "0", "throttle": "0.0",
    "vspd_fpm": "0", "alpha_deg": "0.0",
    "active_aircraft": "", "current_profile": "Default",
    "profiles": "", "timestamp": "0",
}


_xplane_process_cache = None  # cached result: True/False
_xplane_process_cache_time = 0  # timestamp of last check
_XPLANE_PROCESS_CACHE_TTL = 1.0  # seconds between real checks


def _is_xplane_process_running():
    """Check if X-Plane.exe process is running (Windows only).

    Uses a 1-second cache to avoid hammering tasklist 10x/sec.
    Also uses a 3-second grace period: if the process was running and the
    next check fails, we still report True for 3s to handle tasklist delays.
    """
    global _xplane_process_cache, _xplane_process_cache_time
    now = time.time()
    if _xplane_process_cache is not None and (now - _xplane_process_cache_time) < _XPLANE_PROCESS_CACHE_TTL:
        return _xplane_process_cache

    _xplane_process_cache_time = now
    running = False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq X-Plane.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=2
        )
        if "X-Plane.exe" in result.stdout:
            running = True
        else:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq X-Plane-xp11.exe", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=2
            )
            if "X-Plane-xp11.exe" in result.stdout:
                running = True
    except Exception:
        pass

    # Grace period: if previously running and now appears stopped,
    # report True once more to avoid false "off" from tasklist delays
    if _xplane_process_cache is True and not running:
        _xplane_process_cache_time = now
        _xplane_process_cache = None  # force re-check next call
        return True  # one more tick as "running"

    _xplane_process_cache = running
    return running


def _get_xplane_log_path():
    """Get the path to X-Plane's log.txt from prefs.json."""
    try:
        prefs = load_prefs()
        xplane_dir = prefs.get("xplane_path")
        if xplane_dir and os.path.isdir(xplane_dir):
            log_path = os.path.join(xplane_dir, "log.txt")
            if os.path.isfile(log_path):
                return log_path
    except Exception:
        pass
    return None


def _check_xplane_log_loading():
    """Check X-Plane's log.txt to determine if the sim is still loading."""
    log_path = _get_xplane_log_path()
    if not log_path:
        return False
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 2048))
            tail = f.read()
        loading_patterns = [
            "Loading scenery", "Scanning scenery", "Loading world",
            "Loading terrain", "Loading textures", "Loading aircraft",
            "Loading weather", "Reading SAN", "Loading DSF",
            "Compiling shaders", "Loading forests", "Loading buildings",
            "Loading roads", "Loading water", "Loading clouds", "Loading objects",
        ]
        for line in tail.splitlines():
            line_lower = line.lower()
            for pattern in loading_patterns:
                if pattern.lower() in line_lower:
                    return True
    except Exception:
        pass
    return False


def _log_file_recently_modified():
    """Check if X-Plane's log.txt was modified in the last 30 seconds.
    This detects X-Plane startup even before the Lua bridge writes state.txt.
    """
    log_path = _get_xplane_log_path()
    if not log_path:
        return False
    try:
        mtime = os.path.getmtime(log_path)
        return (time.time() - mtime) < 30
    except Exception:
        return False


def get_xplane_state():
    """Determine X-Plane's actual state: 'off', 'loading', or 'ready'.

    Key rule: if the process is running, X-Plane IS running (menu, paused, etc.).
    We only return 'off' when the process is NOT running.
    """
    if not _is_xplane_process_running():
        return "off"

    # Process IS running → X-Plane is active (menu, paused, loading, or ready)
    # Check state.txt for precise sub-state
    ts = None
    try:
        if STATE_FILE.exists():
            for line in STATE_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("timestamp") and "=" in line:
                    _, _, val = line.partition("=")
                    ts = int(val.strip())
                    break
    except Exception:
        pass

    if ts is not None:
        age = time.time() - ts
        if age < 5:
            return "ready"  # fresh data = X-Plane is fully running
        elif age < 10:
            if _check_xplane_log_loading():
                return "loading"
            return "ready"
        else:
            # state.txt >10s old — bridge Lua is paused
            # Could be: menu open, aircraft loading, or closing
            # Show 'loading' in all these cases
            return "loading"

    # No state.txt at all — process is running, likely loading
    return "loading"


def _debug_log_state(data):
    """Write state variables to data/debug_state.txt for troubleshooting."""
    try:
        debug_path = DATA_DIR / "debug_state.txt"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(f"time={time.strftime('%H:%M:%S')}\n")
            f.write(f"xplane_active={data.get('xplane_active', '?')}\n")
            f.write(f"xplane_state={data.get('xplane_state', '?')}\n")
            f.write(f"timestamp_state={data.get('timestamp', '?')}\n")
            if data.get('timestamp'):
                age = time.time() - int(data['timestamp'])
                f.write(f"timestamp_age={age:.1f}s\n")
            process = _is_xplane_process_running()
            f.write(f"process_running={process}\n")
            f.write(f"log_loading={_check_xplane_log_loading()}\n")
            f.write(f"log_recently_modified={_log_file_recently_modified()}\n")
    except Exception:
        pass


def read_state_file():
    data = dict(DEFAULT_STATE)
    if not STATE_FILE.exists():
        data["xplane_active"] = "false"
        data["xplane_state"] = "off"
        _debug_log_state(data)
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
    xplane_state = get_xplane_state()
    data["xplane_state"] = xplane_state
    data["xplane_active"] = "true" if xplane_state == "ready" else "false"
    _debug_log_state(data)
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
        print(f"[Yaw Rescue] Error writing commands: {e}")

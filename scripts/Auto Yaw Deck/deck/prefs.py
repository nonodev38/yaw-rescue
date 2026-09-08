"""Preferences — small persistent settings (web UI language, xplane_path, ...).

Stored server-side so the choice survives X-Plane restarts, IP changes
and is shared by every device connecting to the panel.
"""
import json

from deck.paths import DATA_DIR, PREFS_FILE


def load_prefs():
    """Load saved preferences."""
    defaults = {"lang": "fr"}
    try:
        if PREFS_FILE.exists():
            data = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # Keep lang (validate) and all other keys (xplane_path, etc.)
                result = dict(data)
                if result.get("lang") not in ("fr", "en"):
                    result["lang"] = "fr"
                return result
    except Exception:
        pass
    return defaults


def save_prefs(prefs):
    """Persist preferences to disk."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PREFS_FILE.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[Yaw Rescue] Error writing preferences: {e}")

"""Debug logging shared by the server modules.

Off by default to keep the terminal clean under the QR code banner.
Enable with the --debug CLI flag (server.py) or the YAW_RESCUE_DEBUG=1 env var
(the env var also works when the server is started headless by panel.py).
"""
import os

DEBUG_LOGGING = os.environ.get("YAW_RESCUE_DEBUG", "").strip().lower() in ("1", "true", "yes", "on")


def dlog(msg):
    """Debug logging — prints only when DEBUG_LOGGING is enabled."""
    if DEBUG_LOGGING:
        print(f"[debug] {msg}")


def set_debug(enabled):
    """Toggle debug logging at runtime (used by server.py's --debug flag)."""
    global DEBUG_LOGGING
    DEBUG_LOGGING = bool(enabled)

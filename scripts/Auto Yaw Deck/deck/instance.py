"""Single-instance management for the Tkinter panel (étape P2.4).

Detects and kills previously running panel.py instances (PID file + process
scan) and cleans the PID file up on exit.
"""
import os
import signal
import subprocess
import sys
import time

from deck.paths import DATA_DIR

PID_FILE = DATA_DIR / "panel.pid"


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

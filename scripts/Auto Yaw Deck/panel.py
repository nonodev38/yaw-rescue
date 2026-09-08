#!/usr/bin/env python3
"""
Auto-Yaw Deck — GUI Control Panel
Starts the HTTPS server in a background thread and provides a clean
control panel with X-Plane detection, QR code, and server management.

Usage:
    python panel.py [--port 8443]

Heavy lifting (X-Plane detection, installer, flight resume, instance
management, translations, server runner) lives in the deck_* modules.
This file keeps the Tkinter GUI and the entry point.
"""

import argparse
import os
import sys
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

# --- Local package (created during the P1/P2/P8 splits) ---
from deck import runner
from deck.flight import find_last_airport, start_xplane
from deck.installer import get_install_status, install_auto_yaw_deck, install_flywithlua
from deck.instance import _cleanup_pid_file, _kill_previous_instances
from deck.panel_i18n import PANEL_I18N
from deck.xplane import (XPLANE_EXE_NAMES, _save_xplane_path,
                         clear_deep_search_cache, find_xplane_exe, is_xplane_running)


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
        runner.server_thread = threading.Thread(
            target=runner.run_server,
            args=(self.port, self.no_cert, self.cert_port),
            daemon=True
        )
        runner.server_thread.start()

    def _start_monitoring(self):
        """Periodically check server status and X-Plane."""
        self._check_server()
        self._check_xplane()

    # Cached reference to server module (set once server thread imports it)
    _srv = None

    def _check_server(self):
        if runner.server_error:
            self.status_label.config(text=self.t['status_error'], fg=self.DANGER)
            self.url_label.config(text=runner.server_error)
            return

        if runner.server_started and self._srv is None:
            import server as srv_mod
            self._srv = srv_mod

        if runner.server_started and self._srv:
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
                        text=self.t['install_downloading'], fg=self.ACCENT))
                    ok, msg = install_flywithlua(xplane_dir)
                    if not ok:
                        self.root.after(0, lambda: self._install_done(False, msg))
                        return
                    status = get_install_status(xplane_dir)
                if not status["auto_yaw_deck"] or not status["auto_yaw_lua"]:
                    self.root.after(0, lambda: self.install_status_label.config(
                        text=self.t['install_copying_files'], fg=self.ACCENT))
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
            clear_deep_search_cache()
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
        """Stop the server, close the GUI and terminate the process.

        os._exit(0) is used deliberately: once the Tk root is destroyed and the
        daemon server threads are told to stop, a normal interpreter shutdown
        can still hang on Windows (hidden console, lingering Tk internals).
        Forcing the exit guarantees start_panel.bat hands control back cleanly.
        Only reachable through the real close path (window close button /
        close button) — guarded so a second call is a no-op.
        """
        if getattr(self, "_closed", False):
            return
        self._closed = True
        self.running = False
        _cleanup_pid_file()
        if runner.server_instance:
            try:
                runner.server_instance.shutdown()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass
        # Flush std streams before the forced exit so nothing buffered is lost
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
        hide_console()
        os._exit(0)


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

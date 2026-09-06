# Yaw Rescue v1.2.0 — X-Plane.org Release Notes

> Copy-paste the three sections below into your X-Plane.org download page
> (plain text, no Markdown — the forum strips formatting).

---

## New Version Details

Yaw Rescue v1.2.0 — a major update over the initial v1.0.0 release. This version adds a complete set of live flight instruments around the compass, a flap-retract alert, the ability to resume directly at your last airport, a smarter launcher, and several UI improvements. The web app was also refactored into focused modules for easier maintenance. See "What's New" below for the full list.

---

## What's New

1. LIVE FLIGHT VITALS AROUND THE COMPASS
   - Landing gear strip above the compass: one cell per gear (N / L / R), each showing DN / UP / MID live.
   - Engine RPM and Throttle on the left of the compass.
   - Vertical speed (FPM) and Angle of Attack (AOA) on the right of the compass.
   - Every value is color-coded interactively: gear (green/orange/red), throttle (green up to 70%, orange to 90%, red beyond), FPM (green above -400, red beyond -1,000), AOA (green under 12°, orange to 16°, red above — stall approach).
   - Landing-config alert: the whole gear strip flashes red when any gear is not fully down below 1,000 ft, or when the flap alert is active.
   - Multi-engine aircraft: RPM and throttle show the highest value across all engines.

2. FLAP RETRACT ALERT
   - Uses the aircraft's max flap-extended speed (Vfe) from X-Plane. When airspeed reaches Vfe while the flaps are still extended, the Volets section pulses red and the position badge flashes — even when the section is collapsed. Hysteresis prevents flickering near the threshold.

3. RESUME AT YOUR LAST AIRPORT
   - The control panel reads the last airport (and runway) from X-Plane's own data (Freeflight.prf, with log.txt as fallback).
   - One click on "Start X-Plane" launches the sim directly at that airport with your last aircraft — no menus (requires X-Plane 12.4+; on older versions the sim starts normally). Optional checkbox to disable.

4. SMARTER WINDOWS LAUNCHER
   - start_panel.bat now auto-detects a working Python (py -3 / python / python3, version-checked), checks tkinter, warns if port 8443 is already in use, and prints clear fix instructions if something is missing.

5. UI IMPROVEMENTS
   - Flaps section reworked: now above the trim section, compact diagram, retractable (state remembered per device), live position badge, and preset buttons that auto-highlight the current position.
   - The active tab (Config / Controls / Telemetry) is remembered per device.
   - Language preference (FR/EN) is saved server-side, so it survives X-Plane restarts and IP changes and is shared by every device.

6. MAINTENANCE
   - Web app code reorganized into focused modules (no functional change).
   - Fixed a certificate-generation syntax error that could prevent a fresh server start.

---

## Required

- X-Plane 11 or 12 (Windows / macOS / Linux)
- FlyWithLua NXT plugin (Resources/plugins/FlyWithLua)
- Python 3.7+ with tkinter (for the GUI control panel)
- A smartphone on the same WiFi network as the PC
- Required Python packages (cryptography, qrcode) are installed automatically on first run
- Note: "Resume at last airport" requires X-Plane 12.4+

---

*File: Yaw_Rescue_v1.2.0.zip — version 1.2.0*
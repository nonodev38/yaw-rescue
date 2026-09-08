# Yaw Rescue v1.0.3 — X-Plane.org Release Notes

> Copy-paste the three sections below into your X-Plane.org download page
> (plain text, no Markdown — the forum strips formatting).

---

## New Version Details

Yaw Rescue v1.0.3 — a critical stability update that fixes Lua script loading errors, improves X-Plane state detection, adds web-based X-Plane launch with airport resume, and completes the FR/EN translation of all UI elements. This version resolves the "quarantined scripts" issue that prevented the plugin from working on FlyWithLua NXT 2.8.16.

---

## What's New

1. LUA SCRIPT FIXES — FLYWITHLUA NXT 2.8.16 COMPATIBILITY
   - Fixed 4 dataref errors that caused scripts to be quarantined on every load:
     a. Replaced dataref_table() with dataref() for string datarefs (sim/aircraft/view/acf_descrip and sim/aircraft/present/acf_file — the latter no longer exists in XP12).
     b. Replaced deprecated sim/cockpit2/controls/flap_ratio with sim/cockpit2/controls/flap_handle_request_ratio (writable).
     c. Replaced deprecated sim/flightmodel/position/magpsi with sim/flightmodel/position/mag_psi.
   - Scripts now load without errors on FlyWithLua NXT 2.8.16+.

2. WEB-BASED X-PLANE LAUNCH WITH AIRPORT RESUME
   - The "Launch X-Plane from PC" button on the connection page now reuses the same airport-resume logic as the Python control panel.
   - Reads the last airport and runway from Freeflight.prf (with log.txt fallback), reads the last aircraft, writes data/flight.json, and launches X-Plane.exe --new_flight_json=... — one click to resume your flight.

3. IMPROVED X-PLANE STATE DETECTION
   - Process check is now cached (1-second TTL) to avoid hammering tasklist 10x/sec.
   - Grace period: if the process was running and tasklist reports it stopped, one extra tick is granted before confirming "off".
   - New heuristic: if the process is running but state.txt is older than 10 seconds, the state is "loading" (covers menu open, aircraft loading, or paused sim) instead of "ready" or "off".
   - New function _log_file_recently_modified() detects X-Plane startup even before the Lua bridge writes state.txt.

4. CONNECTION PAGE BUTTON FIXES
   - The "Launch X-Plane" button no longer flickers back during X-Plane startup (launchPending flag blocks setConnected from re-showing it).
   - Button text is only reset when the button becomes visible, not during the launching phase.
   - Button text is correctly translated on language change and page refresh.

5. COMPLETE FR/EN TRANSLATION
   - Added missing i18n keys: diagram.flaps, diagram.flaps_sub, diagram.pitch, diagram.pitch_sub, diagram.roll, diagram.roll_sub, diagram.yaw, diagram.yaw_sub, connect.support.
   - All UI text now switches correctly between French and English.

6. DEBUG LOGGING
   - New data/debug_state.txt file written on every state poll, showing: xplane_active, xplane_state, timestamp age, process_running, log_loading, log_recently_modified.
   - Useful for troubleshooting state detection issues.

7. CACHE BUSTING
   - All JS and CSS references in index.html now include ?v=3 query parameter to force browser cache refresh after updates.

---

## Required

- X-Plane 11 or 12 (Windows / macOS / Linux)
- FlyWithLua NXT plugin (Resources/plugins/FlyWithLua)
- Python 3.7+ with tkinter (for the GUI control panel)
- A smartphone on the same WiFi network as the PC
- Required Python packages (cryptography, qrcode) are installed automatically on first run
- Note: "Resume at last airport" requires X-Plane 12.4+

---

*File: Yaw_Rescue_v1.0.3.zip — version 1.0.3*

---

# Yaw Rescue v1.0.2 — X-Plane.org Release Notes

> Copy-paste the three sections below into your X-Plane.org download page
> (plain text, no Markdown — the forum strips formatting).

---

## New Version Details

Yaw Rescue v1.0.2 — a major update over the initial v1.0.0 release. This version adds a complete set of live flight instruments around the compass, a flap-retract alert, the ability to resume directly at your last airport, a smarter launcher, and several UI improvements. The web app was also refactored into focused modules for easier maintenance. See "What's New" below for the full list.

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

*File: Yaw_Rescue_v1.0.2.zip — version 1.0.2*

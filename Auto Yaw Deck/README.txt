================================================================================
  AUTO-YAW DECK - Fix Your Joystick Yaw Problems
================================================================================

Many joysticks suffer from erratic yaw behavior: jittery potentiometers,
noise near center, and unpredictable oscillations. Auto-Yaw Deck fixes
these issues with professional-grade signal processing, controllable
from your smartphone over WiFi.

================================================================================
  THE PROBLEM WE SOLVE
================================================================================

  Many joysticks (especially budget and mid-range models) have a noisy
  yaw axis that produces:

  - Erratic rudder movements when the stick is centered
  - Rapid oscillations ("jitter") from worn potentiometers
  - Unpredictable yaw jumps during flight

  These issues make coordinated flight difficult and frustrate pilots.
  Auto-Yaw Deck applies professional signal processing to clean up
  the yaw input before it reaches the simulator:

  - Signal smoothing (exponential moving average)
  - Noise filter (rejects rapid oscillations)
  - Dead zone (ignores center jitter)
  - Auto-coordination (compensates yaw in turns)
  - Yaw damper (reduces Dutch roll oscillations)

  All settings are adjustable in real-time from your smartphone.

================================================================================
  ARCHITECTURE
================================================================================

  +-------------+    state.txt     +--------------+    HTTPS/WiFi   +-----------+
  |  X-Plane    | <=============== | Python Server| <=============> | Smartphone|
  | (Lua FWL)   |    commands.txt  | (port 8443)  |   QR code ->   | (browser) |
  +-------------+                  +--------------+                 +-----------+

  1. Lua bridge script reads X-Plane datarefs and writes to data/state.txt
  2. Python server reads state.txt and serves it via REST API (HTTPS)
  3. Smartphone displays live data and sends commands (trims, config, flaps)
  4. Commands are written to data/commands.txt and read by the Lua bridge

================================================================================
  REQUIREMENTS
================================================================================

  - Python 3.7+ (with tkinter for the GUI panel)
  - X-Plane 11/12 with FlyWithLua NXT plugin
  - The auto_yaw.lua script active in Scripts/
  - Both PC and smartphone on the same WiFi network

  Required Python packages are installed automatically on first run:
  - cryptography  (SSL certificate generation)
  - qrcode[pil]   (QR code generation)

================================================================================
  INSTALLATION
================================================================================

  1. Copy the "Auto Yaw Deck" folder into your FlyWithLua Scripts directory:
     X-Plane 12/Resources/plugins/FlyWithLua/Scripts/Auto Yaw Deck/

  2. Place auto_yaw_deck.lua in the Scripts/ folder (NOT inside Auto Yaw Deck/):
     X-Plane 12/Resources/plugins/FlyWithLua/Scripts/auto_yaw_deck.lua
     (FlyWithLua only loads scripts from the root Scripts/ folder)

  3. Launch the control panel:
     Double-click start_panel.bat

  4. Scan the QR code shown in the panel with your phone

  5. Accept the SSL certificate warning in your phone's browser

================================================================================
  FILES
================================================================================

  Scripts/
  +-- auto_yaw_deck.lua          Lua bridge script (must be in Scripts/ root)
  +-- Auto Yaw Deck/
      +-- panel.py               GUI control panel (tkinter)
      +-- server.py              HTTPS server (Python)
      +-- start_panel.bat        Windows launcher
      +-- info.js                Config section info panels
      +-- static/
      |   +-- index.html         Web interface
      |   +-- style.css          Dark aviation theme
      |   +-- app.js             Client-side logic + translations
      +-- data/                  (created automatically)
      |   +-- state.txt          Written by Lua, read by Python
      |   +-- commands.txt       Written by Python, read by Lua
      +-- certs/                 (created automatically)
          +-- server.pem         Self-signed SSL certificate
          +-- server.key         SSL private key

================================================================================
  USAGE - GUI CONTROL PANEL
================================================================================

  Double-click start_panel.bat to launch the control panel.

  The panel shows:
  - Server status (URL, port, HTTPS/HTTP mode)
  - X-Plane detection (running / not running / not found)
  - QR code for quick phone connection
  - "Start X-Plane" button (if detected but not running)
  - "Close Server" button to shut down everything

  Command line options:
    python panel.py                  # HTTPS mode (default)
    python panel.py --no-cert        # HTTP mode (testing only)
    python panel.py --port 9000      # Custom port

  The console window auto-minimizes when the panel opens.

================================================================================
  USAGE - COMMAND LINE SERVER
================================================================================

  You can also start the server directly without the GUI panel:

    python server.py                  # HTTPS mode (default)
    python server.py --no-cert        # HTTP mode (testing only)
    python server.py --port 9000      # Custom port

  The server displays a QR code in the terminal that you can scan with your phone.

================================================================================
  WEB INTERFACE FEATURES
================================================================================

  The mobile web interface has 3 tabs:

  --- CONFIG TAB (default) ---

    Lissage du signal (Signal Smoothing)
      Exponential moving average filter for the joystick input.
      Factor: 0.01 (strong) to 0.50 (weak). Default: 0.15

    Filtre anti-bruit (Noise Filter)
      Rejects rapid joystick oscillations (potentiometer jitter).
      Threshold: 0.00 (off) to 0.30 (aggressive). Default: 0.05

    Zone morte (Dead Zone)
      Ignores small movements near the center of the joystick axis.
      Size: 0.00 (off) to 0.20. Default: 0.03

    Auto-Coordination
      Automatically applies yaw correction proportional to bank angle.
      Gain: 0.00 (off) to 1.00. Default: 0.40
      Bank limit: 5 to 60 degrees. Default: 35

    Yaw Damper
      Reduces yaw oscillations (Dutch roll) using rotation rate feedback.
      Gain: 0.00 (off) to 1.00. Default: 0.30
      Sensitivity: 0.5 to 5.0. Default: 2.0

    Options (toggles)
      Enable/disable plugin, smoothing, dead zone, auto-coordination, yaw damper

    Each section has an info button (i) that opens a detailed explanation panel.

  --- CONTROLS TAB ---

    Compass
      Real-time compass with rotating rose and fixed lubber line.
      Shows current magnetic heading from X-Plane.

    Return Heading
      "Return heading" button freezes the current heading and displays
      a yellow arrow at the reciprocal direction (180 degrees opposite).
      Useful for returning to the departure airport.
      - First click: records heading and shows arrow
      - Second click: hides arrow (preserves heading)
      - "Clear" button: resets to record a new heading

    Trim Sliders
      - Pitch (elevator): -1.0 to +1.0
      - Roll (aileron): -1.0 to +1.0
      - Yaw (rudder): -1.0 to +1.0
      Trim values are applied as direct offsets to the control surfaces,
      which works on ALL aircraft (including those without trim tabs).

    Flaps
      - Slider from 0% to 100%
      - Preset buttons: 0%, 1/3, 2/3, Full

  --- TELEMETRY TAB ---

    Flight Data
      - Heading (degrees)
      - Altitude (feet)
      - Airspeed (knots)
      - Bank angle (degrees)

    Auto-Yaw State
      - Raw input, Smoothed input, Final output
      - Auto-coordination output, Damper output
      - Active profile name

    Aircraft
      - Detected aircraft name from X-Plane

================================================================================
  BIDIRECTIONAL SYNCHRONIZATION
================================================================================

  Changes made on the smartphone are reflected in the FlyWithLua panel
  and vice versa. Both panels read from the same global config table.

  X-Plane -> Web:
    auto_yaw.lua updates config -> auto_yaw_deck.lua writes to state.txt
    -> Python serves via API -> Web polls and displays

  Web -> X-Plane:
    Web sends command -> commands.txt -> auto_yaw_deck.lua sets config
    -> auto_yaw.lua reads config every frame -> applies to controls

  All settings are also saved to AutoYaw_profiles.cfg for persistence.

================================================================================
  LANGUAGE SUPPORT
================================================================================

  The interface supports French (FR) and English (EN).

  Toggle language with the EN/FR button in the header.
  Language preference is saved in localStorage and restored on reload.

  All UI elements are translated:
  - Tab labels, card headers, slider labels
  - Connection page text
  - Status badges (OFFLINE / WAITING / LIVE)
  - Config section info panels

================================================================================
  TRIM SYSTEM - HOW IT WORKS
================================================================================

  Traditional X-Plane trim datarefs only work on aircraft that have physical
  trim tabs (like the elevator THS on the Cessna 172). Aircraft without
  aileron or rudder trim tabs ignore those datarefs entirely.

  Auto-Yaw Deck solves this by applying trim values as DIRECT OFFSETS to
  the joystick override outputs (sim/joystick/yoke_*_ratio):

    pitch_output = raw_pitch + elevator_trim
    roll_output  = raw_roll  + aileron_trim
    yaw_output   = yaw_auto  + rudder_trim

  This approach works universally on ALL aircraft in X-Plane.

================================================================================
  X-PLANE DETECTION
================================================================================

  The server detects X-Plane by checking the timestamp field in state.txt.
  The Lua bridge writes os.time() every frame, so if the timestamp is
  within 5 seconds of the current time, X-Plane is considered active.

  The web interface shows three connection states:
    OFFLINE (red)    - No connection to the server
    WAITING (orange) - Server running, X-Plane not detected
    LIVE (green)     - Server + X-Plane both active

  When a new aircraft is loaded, the return heading is automatically
  reset and re-recorded at the new heading.

================================================================================
  NOISE FILTER - HOW IT WORKS
================================================================================

  Joystick potentiometers often produce rapid oscillations ("jitter"),
  especially near the center position. The noise filter detects these by
  comparing consecutive raw values:

    If |current_raw - previous_raw| > threshold:
        Reject the input, keep the previous smoothed value
    Else:
        Apply normal smoothing

  This eliminates jitter without affecting real, deliberate movements.

  Tuning tips:
    0.00 = off (no filtering)
    0.05 = default (good for most joysticks)
    0.10-0.15 = aggressive (for very noisy potentiometers)

================================================================================
  SSL CERTIFICATE
================================================================================

  The server auto-generates a self-signed SSL certificate using the
  Python 'cryptography' library. The certificate includes:
    - RSA-2048 key pair
    - X.509 v3 with Subject Alternative Names (all local IPs)
    - Valid for 365 days

  If your phone blocks the certificate:
    1. Open http://YOUR_PC_IP:8080/cert in your phone browser
    2. Download autoyawdeck-ca.pem
    3. Android: Settings > Security > Install certificate > CA certificate
    4. Reopen the HTTPS URL — the certificate is now trusted

  The cert download server runs on a separate HTTP port (default: 8080)
  specifically to allow certificate installation without TLS warnings.

================================================================================
  TROUBLESHOOTING
================================================================================

  Server won't start:
    - Check Python version: python --version (needs 3.7+)
    - Check if port 8443 is already in use
    - Try --no-cert mode for testing

  Phone can't connect:
    - Ensure PC and phone are on the same WiFi network
    - Not using mobile data or a phone hotspot
    - Accept the SSL certificate warning in the browser

  Samsung / Knox blocks the certificate:
    - Follow the SSL certificate section above
    - Install the CA certificate from the HTTP download page

  No data showing on the phone:
    - Verify auto_yaw_deck.lua is in Scripts/ root (not in Auto Yaw Deck/)
    - Check data/state.txt is being updated (check X-Plane console logs)
    - Check the Python server console for errors

  Trim sliders don't affect the aircraft:
    - Ensure auto_yaw.lua is loaded and the plugin is enabled
    - Check that the override is active (ACTIVE status in FlyWithLua panel)
    - The trim system works by applying offsets to the joystick override,
      so the plugin must be enabled for trims to have effect

================================================================================
  SECURITY
================================================================================

  - Self-signed SSL certificate for encrypted local communication
  - Server listens only on the local network (LAN)
  - No data is sent to the internet
  - Commands are validated by the Lua bridge before application
  - Certificate auto-expires after 365 days (auto-regenerated on next start)

================================================================================
  COMMAND LINE OPTIONS
================================================================================

  server.py:
    --port PORT        HTTPS port (default: 8443)
    --cert-port PORT   HTTP port for cert download (default: 8080)
    --cert-dir DIR     Certificate directory (default: certs/)
    --no-cert          HTTP-only mode (no SSL)

  panel.py:
    --port PORT        HTTPS port (default: 8443)
    --cert-port PORT   HTTP port for cert download (default: 8080)
    --no-cert          HTTP-only mode (no SSL)

================================================================================

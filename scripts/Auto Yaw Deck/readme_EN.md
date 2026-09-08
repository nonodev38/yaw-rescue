<div align="center">

# ✈️ AUTO-YAW DECK

### 🎮 *X-Plane Remote Control via Smartphone*

<img src="logo.png" alt="Auto-Yaw Deck" width="160"/>

**Fix your yaw. Fly your plane. 🛩️ Control everything from your phone.**

<span style="color:#22b8a6">✅ Works on X-Plane 11 & 12</span> • <span style="color:#3b82f6">📱 Smartphone web UI</span> • <span style="color:#f59e0b">🇫🇷 🇬🇧 FR / EN</span> • <span style="color:#ef4444">🔒 100% local, SSL encrypted</span>

---

</div>

> 🎯 **What is it?**
>
> Monitor **live telemetry**, adjust **trims**, configure **Auto-Yaw filters**, manage your **flaps & gear** — all from a clean, dark-themed mobile web interface, over your own WiFi. No internet, no cloud, no data leaving your network.

---

## 🧭 Table of Contents

| | |
|---|---|
| 1️⃣ [Architecture](#-architecture) | 9️⃣ [Trim system](#-trim-system--how-it-works) |
| 2️⃣ [Requirements](#-requirements) | 🔟 [X-Plane detection](#-x-plane-detection) |
| 3️⃣ [Installation](#-installation) | 1️⃣1️⃣ [Noise filter explained](#-noise-filter--how-it-works) |
| 4️⃣ [File structure](#-file-structure) | 1️⃣2️⃣ [SSL certificate](#-ssl-certificate) |
| 5️⃣ [GUI control panel](#-usage--gui-control-panel) | 1️⃣3️⃣ [Troubleshooting](#-troubleshooting) |
| 6️⃣ [Command line server](#-usage--command-line-server) | 1️⃣4️⃣ [Security](#-security) |
| 7️⃣ [Web interface features](#-web-interface-features) | 1️⃣5️⃣ [CLI options](#-command-line-options) |
| 8️⃣ [Bidirectional sync](#-bidirectional-synchronization) | |

---

## 🧱 Architecture

```
+-------------+   state.txt    +--------------+   HTTPS/WiFi   +-----------+
|  ✈️ X-Plane  | <=============> | 🐍 Python    | <============> | 📱 Phone  |
|  (Lua FWL)  |   commands.txt  | Server       |   QR code ->   | (browser) |
+-------------+                | (port 8443)  |                +-----------+
                               +--------------+
```

**How data flows:**

1. 🟦 The **Lua bridge** reads X-Plane datarefs → writes to `data/state.txt`
2. 🟩 The **Python server** reads `state.txt` → serves it via REST API (HTTPS)
3. 🟨 Your **smartphone** displays live data & sends commands (trims, config, flaps)
4. 🟥 Commands are written to `data/commands.txt` → read by the Lua bridge

---

## ✅ Requirements

| Requirement | Note |
|---|---|
| <span style="color:#22b8a6">🐍 **Python 3.7+**</span> | with `tkinter` for the GUI panel |
| <span style="color:#3b82f6">✈️ **X-Plane 11 / 12**</span> | with the FlyWithLua NXT plugin |
| <span style="color:#3b82f6">📜 **`auto_yaw.lua` active**</span> | in the FlyWithLua `Scripts/` folder |
| <span style="color:#f59e0b">📶 **Same WiFi network**</span> | PC + smartphone |

> 📦 Python packages are **installed automatically on first run**:
> `cryptography` (SSL certificate) + `qrcode[pil]` (QR code)

---

## 📥 Installation

**1️⃣** Copy the `Auto Yaw Deck` folder into your FlyWithLua Scripts directory:

```
X-Plane 12/Resources/plugins/FlyWithLua/Scripts/Auto Yaw Deck/
```

**2️⃣** Place `auto_yaw_deck.lua` in the `Scripts/` folder — **NOT** inside `Auto Yaw Deck/`:

```
X-Plane 12/Resources/plugins/FlyWithLua/Scripts/auto_yaw_deck.lua
```

> ⚠️ **Important:** FlyWithLua only loads scripts from the **root** `Scripts/` folder!

**3️⃣** Launch the control panel → double-click **`start_panel.bat`** 🖱️

**4️⃣** Scan the 📱 **QR code** shown in the panel

**5️⃣** Accept the 🔐 **SSL certificate warning** in your phone's browser

---

## 🗂️ File Structure

```
Scripts/
├── auto_yaw_deck.lua          🟦 Lua bridge (must be in Scripts/ root)
└── Auto Yaw Deck/
    ├── panel.py               🖥️  GUI control panel (tkinter)
    ├── server.py              🐍 HTTPS server (Python)
    ├── start_panel.bat        🪟 Windows launcher
    ├── info.js                ℹ️  Config section info panels
    ├── static/
    │   ├── index.html         🌐 Web interface
    │   ├── style.css          🎨 Dark aviation theme
    │   ├── config.js          ⚙️  Tunable constants (polling, debounce)
    │   ├── i18n.js            🌍 Translations (FR/EN) + language mgmt
    │   ├── state.js           📊 State polling + local-change guard
    │   ├── api.js             📡 Server command sending
    │   ├── sliders.js         🎚️  Slider widgets (steps, center, diagrams)
    │   ├── ui.js              🧩 DOM refs, tabs, navigation, status
    │   ├── compass.js         🧭 Compass + return heading
    │   ├── actions.js         🔘 Reset trims / flaps actions
    │   └── main.js            🚀 Bootstrap (init + cleanup)
    ├── data/                  ⚙️  (created automatically)
    │   ├── state.txt          📝 Written by Lua, read by Python
    │   ├── commands.txt       📝 Written by Python, read by Lua
    │   ├── prefs.json         💾 Saved preferences (web UI language…)
    │   └── flight.json        🛫 Generated when resuming at last airport
    └── certs/                 🔐 (created automatically)
        ├── server.pem         🔑 Self-signed SSL certificate
        └── server.key         🔑 SSL private key
```

---

## 🖥️ Usage — GUI Control Panel

Double-click **`start_panel.bat`** and the panel shows you everything:

| Display | Description |
|---|---|
| 📡 **Server status** | URL, port, HTTPS/HTTP mode |
| 🎮 **X-Plane detection** | running ✅ / not running ⚠️ / not found ❌ |
| 🛫 **Last airport** | from `Freeflight.prf` (+ `log.txt` fallback), with a *« Reprendre au dernier aéroport »* checkbox (✅ by default) |
| 📱 **QR code** | instant phone connection |
| ▶️ **Start X-Plane** | only when detected but not running — resumes at the last airport if the box is checked |
| ⏹️ **Close Server** | shuts everything down |

### 🛫 Resume at your last airport

When X-Plane isn't running, the panel reads the airport (and runway 🛬) from the last session:

1. `Output/preferences/Freeflight.prf` (`_last_start` / `_airport`)
2. `log.txt` — last `I/FLT: Init … apt:XXXX` line

Clicking **« Démarrer X-Plane »** launches the sim with:

```bash
--new_flight_json=<data/flight.json>
```

…so X-Plane starts **directly at that airport** ✈️ (requires **X-Plane 12.4+**). Uncheck the box to start at the default location.

### 🖥️ Panel command line

```bash
python panel.py              # 🔒 HTTPS mode (default)
python panel.py --no-cert    # 🚫 HTTP mode (testing only)
python panel.py --port 9000  # 🔢 Custom port
```

> 🤫 The console window **auto-minimizes** when the panel opens — that's normal!

---

## 💻 Usage — Command Line Server

No GUI? Start the server directly:

```bash
python server.py              # 🔒 HTTPS mode (default)
python server.py --no-cert    # 🚫 HTTP mode (testing only)
python server.py --port 9000  # 🔢 Custom port
```

> 📱 The server prints a **QR code right in the terminal** — scan it with your phone.

---

## 🌐 Web Interface Features

The mobile web UI has **3 tabs** 🗂️:

### ⚙️ CONFIG TAB *(default)*

| Setting | What it does | Range | Default |
|---|---|---|---|
| 🎚️ **Lissage du signal** *(Signal Smoothing)* | Exponential moving average filter | 0.01 (strong) → 0.50 (weak) | `0.15` |
| 🧹 **Filtre anti-bruit** *(Noise Filter)* | Rejects rapid joystick jitter | 0.00 (off) → 0.30 (aggressive) | `0.05` |
| 🎯 **Zone morte** *(Dead Zone)* | Ignores small center movements | 0.00 (off) → 0.20 | `0.03` |
| 🔄 **Auto-Coordination** | Yaw correction ∝ bank angle — gain / bank limit | 0.00–1.00 / 5–60° | `0.40` / `35` |
| 🌀 **Yaw Damper** | Reduces Dutch roll via rotation-rate feedback — gain / sensitivity | 0.00–1.00 / 0.5–5.0 | `0.30` / `2.0` |

**Options (toggles):** enable/disable the plugin, smoothing, dead zone, auto-coordination & yaw damper.

> ℹ️ Every section has an info button **(i)** that opens a detailed explanation panel.

### 🎛️ CONTROLS TAB

- 🧭 **Compass** — real-time rotating rose + fixed lubber line, shows magnetic heading
- 🔙 **Return Heading** — freeze the current heading, a yellow arrow points to the **reciprocal** (180°). *First click* records + shows, *second click* hides, **Clear** resets.
- 🎚️ **Trim Sliders** — Pitch 🡕 / Roll 🡘 / Yaw 🡔 between **−1.0 and +1.0**, applied as direct offsets → works on **ALL** aircraft (even without trim tabs!)
- 🦅 **Flaps** — slider 0–100% + preset buttons `0% / 1/3 / 2/3 / Full`

### 📡 TELEMETRY TAB

| Data | Readout |
|---|---|
| 🧭 **Flight data** | Heading (°), Altitude (ft), Airspeed (kts), Bank (°) |
| ⚙️ **Auto-Yaw state** | Raw / Smoothed / Final output, Auto-coord & Damper output, active profile |
| ✈️ **Aircraft** | Name detected by X-Plane |

---

## 🔄 Bidirectional Synchronization

Whatever you change on your **phone** is reflected in the **FlyWithLua panel** — and vice-versa. Both read the same global config table.

```
X-Plane → Web:   auto_yaw.lua → state.txt → Python API → Web display
Web → X-Plane:   Web command → commands.txt → auto_yaw_deck.lua → auto_yaw.lua
```

> 💾 All settings are also saved to `AutoYaw_profiles.cfg` for persistence.

---

## 🌍 Language Support

> 🇫🇷 **Français** &nbsp;|&nbsp; 🇬🇧 **English** — toggle with the **EN/FR** button in the header.

The preference is saved **both** in the browser (`localStorage`) **and** server-side in `data/prefs.json`, so it survives:
- 🔄 X-Plane restarts
- 🌐 IP address changes
- 📱 **every device** connecting to the panel

Everything is translated: tab labels, card headers, sliders, connection page, status badges, info panels.

---

## 🎚️ Trim System — How It Works

> ❌ Traditional X-Plane trim datarefs only work on aircraft with **physical trim tabs** (e.g. the Cessna 172's elevator THS). Aircraft without aileron/rudder trim tabs **ignore** those datarefs.

✅ **Auto-Yaw Deck** applies trim values as **DIRECT OFFSETS** on the joystick override outputs (`sim/joystick/yoke_*_ratio`):

```
pitch_output = raw_pitch + elevator_trim   🡕  Tangage
roll_output  = raw_roll  + aileron_trim    🡘  Roulis
yaw_output   = yaw_auto  + rudder_trim     🡔  Lacet
```

> 🎉 This works **universally on ALL aircraft** in X-Plane!

---

## 📡 X-Plane Detection

The server checks the **timestamp** in `state.txt` (the Lua bridge writes `os.time()` every frame). If it's fresher than **5 seconds**, X-Plane is considered **active**.

| Status | Color | Meaning |
|---|---|---|
| 🟥 **OFFLINE** | red | No connection to the server |
| 🟧 **WAITING** | orange | Server running, X-Plane not detected |
| 🟩 **LIVE** | green | Server + X-Plane both active |

> ✈️ When a new aircraft loads, the return heading resets & re-records automatically.

---

## 🧹 Noise Filter — How It Works

Joystick potentiometers produce rapid **oscillations** ("jitter"), especially near center. The filter compares consecutive raw values:

```
If |current_raw − previous_raw| > threshold:
    🚫 Reject the input → keep the previous smoothed value
Else:
    ✅ Apply normal smoothing
```

**Tuning tips:**

| Value | Effect |
|---|---|
| `0.00` | 🚫 Off (no filtering) |
| `0.05` | 👍 Default — good for most joysticks |
| `0.10–0.15` | 💪 Aggressive — for very noisy potentiometers |

---

## 🔐 SSL Certificate

The server auto-generates a **self-signed SSL certificate** (Python `cryptography` lib):
- 🔑 RSA-2048 key pair
- 📜 X.509 v3 with Subject Alternative Names (**all local IPs**)
- ⏳ Valid for **365 days**

**Phone blocking the certificate?**

1. 📲 Open `http://YOUR_PC_IP:8080/cert` in the phone's browser
2. ⬇️ Download `autoyawdeck-ca.pem`
3. 🛡️ *Android:* Settings > Security > Install certificate > **CA certificate**
4. 🔁 Reopen the HTTPS URL — now trusted!

> 🌐 The cert download server runs on a **separate HTTP port** (default `8080`) so you can install the certificate without TLS warnings.

---

## 🛠️ Troubleshooting

<details>
<summary><b>🛑 Server won't start?</b></summary>

- ✅ `start_panel.bat` **auto-detects Python** (`py -3` / `python` / `python3`), checks tkinter & prints clear fix instructions
- 🐍 Check the Python version: `python --version` (needs **3.7+**)
- 🔌 Is **port 8443** already in use? (the launcher warns you)
- 🧪 Try `--no-cert` mode for testing

</details>

<details>
<summary><b>📱 Phone can't connect?</b></summary>

- 📶 PC & phone must be on the **same WiFi network**
- 🚫 Not using mobile data or a phone hotspot
- 🔐 Accept the SSL certificate warning in the browser

</details>

<details>
<summary><b>🛡️ Samsung / Knox blocks the certificate?</b></summary>

- 📖 Follow the [SSL certificate](#-ssl-certificate) section above
- 📲 Install the CA certificate from the HTTP download page

</details>

<details>
<summary><b>👻 No data showing on the phone?</b></summary>

- 📂 Verify `auto_yaw_deck.lua` is in the `Scripts/` root (not in `Auto Yaw Deck/`)
- 📝 Check `data/state.txt` is being updated (see X-Plane console logs)
- 🖥️ Check the Python server console for errors

</details>

<details>
<summary><b>🎚️ Trim sliders don't affect the aircraft?</b></summary>

- 📜 Ensure `auto_yaw.lua` is loaded and the plugin is **enabled**
- ✅ Check the override is active (**ACTIVE** status in the FlyWithLua panel)
- 🔧 Trims work as offsets on the joystick override → the plugin **must be enabled**

</details>

---

## 🔒 Security

| | |
|---|---|
| 🔐 | Self-signed SSL certificate for encrypted local communication |
| 🌐 | Server listens **only** on the local network (LAN) |
| 🚫 | No data is ever sent to the internet |
| 🛡️ | Commands validated by the Lua bridge before application |
| ⏳ | Certificate auto-expires after 365 days (auto-regenerated on next start) |

---

## ⚙️ Command Line Options

**`server.py`:**

| Option | Description | Default |
|---|---|---|
| `--port PORT` | HTTPS port | `8443` |
| `--cert-port PORT` | HTTP port for cert download | `8080` |
| `--cert-dir DIR` | Certificate directory | `certs/` |
| `--no-cert` | HTTP-only mode (no SSL) | — |

**`panel.py`:**

| Option | Description | Default |
|---|---|---|
| `--port PORT` | HTTPS port | `8443` |
| `--cert-port PORT` | HTTP port for cert download | `8080` |
| `--no-cert` | HTTP-only mode (no SSL) | — |

---

<div align="center">

### ✈️ Happy flying — and enjoy that perfectly smooth yaw! 🛩️

<img src="logo.png" alt="Auto-Yaw Deck" width="80"/>

</div>

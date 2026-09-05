# ✈️ Yaw Rescue

> **Fix your joystick yaw problems** — Professional signal processing for X-Plane, controllable from your smartphone.

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=flat&logo=python&logoColor=white)
![X-Plane](https://img.shields.io/badge/X--Plane-11%2F12-000000?style=flat)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 The Problem

Many joysticks suffer from **erratic yaw behavior**:

- 🎢 Jittery potentiometers that send noise near center
- ⚡ Rapid oscillations that make coordinated flight impossible
- 🔄 Unpredictable rudder jumps during flight

**Yaw Rescue fixes all of these** with professional-grade signal processing, controllable from your smartphone over WiFi.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📱 **Smartphone Control** | Full remote control panel from your phone — no need to alt-tab |
| 🔧 **Signal Smoothing** | Exponential moving average to reduce input noise |
| 🔇 **Noise Filter** | Rejects rapid joystick oscillations (potentiometer jitter) |
| ⭕ **Dead Zone** | Ignores center jitter around the stick's neutral position |
| 🔄 **Auto-Coordination** | Automatic yaw correction during bank turns |
| 🛑 **Yaw Damper** | Reduces Dutch roll oscillations like an airliner autopilot |
| 🧭 **Live Compass** | Real-time heading with return heading marker |
| 🌐 **FR/EN** | Full bilingual support (French + English) |
| 🔒 **100% Local** | No internet connection — your data stays on your network |

## 🚀 Quick Start

### 1. Install

Copy these **3 items** into your FlyWithLua `Scripts/` folder:

```
X-Plane/Resources/plugins/FlyWithLua/Scripts/
├── auto_yaw.lua              ← Main script
├── auto_yaw_deck.lua         ← Bridge to Python server
└── Auto Yaw Deck/            ← Python server + web app
```

### 2. Start

```
Double-click Auto Yaw Deck/start_panel.bat
```

### 3. Connect

1. 📱 Scan the QR code with your phone
2. ✅ Accept the SSL certificate warning
3. 🎮 Done! Adjust settings from your smartphone

> ⚠️ **Important:** `auto_yaw.lua` and `auto_yaw_deck.lua` must be **directly** in `Scripts/` (not inside the `Auto Yaw Deck/` subfolder). FlyWithLua only loads scripts from the root folder.

## 📂 File Structure

```
Scripts/
├── auto_yaw.lua              ← Main script (FlyWithLua)
├── auto_yaw_deck.lua         ← Bridge to Python server
├── AutoYaw_profiles.cfg      ← Settings (auto-created)
├── README.txt                ← This file
└── Auto Yaw Deck/
    ├── panel.py              ← GUI control panel
    ├── server.py             ← HTTPS server
    ├── translations.lua      ← FlyWithLua UI translations
    ├── start_panel.bat       ← Windows launcher
    ├── static/
    │   ├── index.html        ← Web interface
    │   ├── style.css         ← Dark aviation theme
    │   ├── app.js            ← Client logic + translations
    │   ├── info.js           ← Config info panels
    │   └── readme.js         ← User manual content
    ├── data/                 ← Auto-created
    │   ├── state.txt         ← Lua → Python
    │   └── commands.txt      ← Python → Lua
    └── certs/                ← Auto-created
        ├── server.pem        ← SSL certificate
        └── server.key        ← SSL private key
```

## 🎛️ How It Works

```
┌─────────────┐    state.txt     ┌──────────────┐    HTTPS    ┌─────────────┐
│  X-Plane    │ <=============== │ Python Server │ <=========> │  Smartphone │
│  (Lua FWL)  │    commands.txt  │  (port 8443)  │   QR code   │  (browser)  │
└─────────────┘                  └──────────────┘             └─────────────┘
```

1. **Lua bridge** reads X-Plane datarefs and writes to `state.txt`
2. **Python server** reads state and serves via REST API (HTTPS)
3. **Smartphone** displays live data and sends commands
4. **Lua bridge** reads commands and applies them to X-Plane

## 🎮 Trim System

Traditional X-Plane trim datarefs only work on aircraft with physical trim tabs. **Yaw Rescue** applies trim as **direct offsets** to the joystick override:

```
pitch_output = raw_pitch + elevator_trim
roll_output  = raw_roll  + aileron_trim
yaw_output   = yaw_auto  + rudder_trim
```

**This works on ALL aircraft**, even those without aileron or rudder trim tabs.

## 🧭 Return Heading

The compass includes a **return heading** feature:

1. Press "Return heading" to freeze the current heading
2. A yellow arrow appears at the **reciprocal direction** (180°)
3. Follow the arrow to return to your departure airport
4. Auto-resets when a new aircraft is loaded

## 📱 Mobile Interface

Three tabs in the web interface:

### ⚙️ Config
- Signal smoothing factor
- Noise filter threshold
- Dead zone size
- Auto-coordination gain
- Yaw damper gain + sensitivity
- All toggles (enable/disable each feature)

### 🎛️ Controls
- Live compass with rotating rose
- Return heading marker
- Trim sliders (pitch, roll, yaw)
- Flap position slider + presets

### 📡 Telemetry
- Heading, altitude, airspeed, bank
- Auto-Yaw internal state (raw, smoothed, output)
- Active profile name
- Detected aircraft

## 🔒 Security

- **100% local** — no data sent to the internet
- **Self-signed SSL** certificate for encrypted communication
- **Server listens only** on your local network (LAN)
- **Commands validated** by Lua bridge before application
- Certificate **auto-expires** after 365 days

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Script not loading | Check files are in `Scripts/` root, not in subfolder |
| Server won't start | Run `python --version` (needs 3.7+), packages auto-install |
| Phone can't connect | Same WiFi network, accept SSL warning |
| Samsung blocks cert | Install CA cert from `http://PC_IP:8080/cert` |
| No data showing | Check `auto_yaw_deck.lua` is loaded in FlyWithLua |
| Sliders flicker | Fixed in latest version — update all files |

## 📋 Requirements

- **Python 3.7+** (with tkinter for GUI panel)
- **X-Plane 11/12** with FlyWithLua NXT
- **Same WiFi network** for PC and smartphone
- Python packages are **auto-installed** on first run

## 📄 License

MIT License — free to use and modify.

---

<p align="center">
  Made with ❤️ for X-Plane pilots
</p>

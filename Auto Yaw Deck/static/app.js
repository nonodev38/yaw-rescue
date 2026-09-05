/**
 * AUTO-YAW DECK — Client-side application
 * Handles polling for state updates, sending commands, and UI interactions.
 */

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const POLL_INTERVAL = 150;       // ms between state polls
const COMMAND_DEBOUNCE = 200;    // ms before sending slider changes

// ---------------------------------------------------------------------------
// Translations
// ---------------------------------------------------------------------------
const I18N = {
    fr: {
        // Status
        'status.offline': 'HORS LIGNE',
        'status.live': 'EN DIRECT',
        'status.connected': 'Connecté à X-Plane',
        'status.disconnected': 'En attente de connexion X-Plane...',
        'status.waiting': 'EN ATTENTE',
        'status.server_only': 'Serveur actif — X-Plane non détecté',
        // Connection page
        'connect.subtitle': 'Corrigez les problèmes de',
        'connect.subtitle2': 'de votre joystick',
        'connect.subtitle3': 'Pilotage X-Plane depuis votre smartphone',
        'connect.scan': "Scannez le QR code ou ouvrez l'adresse ci-dessus sur votre téléphone",
        'connect.status': 'Scannez le QR code avec votre telephone',
        'connect.enter': 'Entrer dans le cockpit →',
        'connect.manual': 'Manuel utilisateur',
        'connect.privacy': '100% local — aucune donnée envoyée sur Internet. Corrigez le yaw erratique de votre joystick grâce au lissage, filtre anti-bruit et zone morte.',
        // Tabs
        'tab.config': '⚙️ Config',
        'tab.controls': '🎛️ Contrôles',
        'tab.telemetry': '📡 Télémétrie',
        // Config
        'config.smoothing': 'Lissage du signal',
        'config.smoothing_factor': 'Facteur de lissage',
        'config.noise': 'Filtre anti-bruit',
        'config.noise_threshold': 'Seuil anti-bruit',
        'config.deadzone': 'Zone morte',
        'config.deadzone_size': 'Taille zone morte',
        'config.autocoord': 'Auto-Coordination',
        'config.coord_gain': 'Gain de coordination',
        'config.bank_limit': 'Limite de bank (DEG)',
        'config.damper': 'Yaw Damper',
        'config.damper_gain': 'Gain du damper',
        'config.sensitivity': 'Sensibilité',
        'config.options': 'Options',
        'config.enable': 'Activer le plugin',
        'config.smoothing_on': 'Lissage',
        'config.deadzone_on': 'Zone morte',
        'config.autocoord_on': 'Auto-coordination',
        'config.damper_on': 'Yaw damper',
        // Controls
        'controls.trim': 'Trim',
        'controls.pitch': 'Profondeur (Pitch)',
        'controls.roll': 'Ailerons (Roll)',
        'controls.yaw': 'Direction (Yaw)',
        'controls.reset_trims': '↺ Réinitialiser trims',
        'controls.flaps': 'Volets',
        'controls.flap_pos': 'Position volets',
        'controls.return_heading': 'Cap retour',
        'controls.clear': 'Effacer',
        // Telemetry
        'telemetry.flight': 'Vol en cours',
        'telemetry.heading': 'Cap',
        'telemetry.altitude': 'Altitude',
        'telemetry.airspeed': 'Vitesse',
        'telemetry.bank': 'Banque',
        'telemetry.autoyaw': 'Auto-Yaw',
        'telemetry.raw': 'Entrée brute',
        'telemetry.smoothed': 'Lissée',
        'telemetry.output': 'Sortie finale',
        'telemetry.coord': 'Coord auto',
        'telemetry.damper': 'Damper',
        'telemetry.profile': 'Profil',
        'telemetry.aircraft': 'Avion',
        'telemetry.no_aircraft': 'Aucun avion détecté',
    },
    en: {
        // Status
        'status.offline': 'OFFLINE',
        'status.live': 'LIVE',
        'status.connected': 'Connected to X-Plane',
        'status.disconnected': 'Waiting for X-Plane connection...',
        'status.waiting': 'WAITING',
        'status.server_only': 'Server active — X-Plane not detected',
        // Connection page
        'connect.subtitle': 'Fix your joystick',
        'connect.subtitle2': 'problems',
        'connect.subtitle3': 'Control X-Plane from your smartphone',
        'connect.scan': 'Scan the QR code or open the address above on your phone',
        'connect.status': 'Scan the QR code with your phone',
        'connect.enter': 'Enter the cockpit →',
        'connect.manual': 'User manual',
        'connect.privacy': '100% local — no data sent to the Internet. Fix erratic joystick yaw with smoothing, noise filter, and dead zone.',
        // Tabs
        'tab.config': '⚙️ Config',
        'tab.controls': '🎛️ Controls',
        'tab.telemetry': '📡 Telemetry',
        // Config
        'config.smoothing': 'Signal Smoothing',
        'config.smoothing_factor': 'Smoothing factor',
        'config.noise': 'Noise Filter',
        'config.noise_threshold': 'Noise threshold',
        'config.deadzone': 'Dead Zone',
        'config.deadzone_size': 'Dead zone size',
        'config.autocoord': 'Auto-Coordination',
        'config.coord_gain': 'Coordination gain',
        'config.bank_limit': 'Bank limit (DEG)',
        'config.damper': 'Yaw Damper',
        'config.damper_gain': 'Damper gain',
        'config.sensitivity': 'Sensitivity',
        'config.options': 'Options',
        'config.enable': 'Enable plugin',
        'config.smoothing_on': 'Smoothing',
        'config.deadzone_on': 'Dead zone',
        'config.autocoord_on': 'Auto-coordination',
        'config.damper_on': 'Yaw damper',
        // Controls
        'controls.trim': 'Trim',
        'controls.pitch': 'Pitch (Elevator)',
        'controls.roll': 'Roll (Ailerons)',
        'controls.yaw': 'Yaw (Rudder)',
        'controls.reset_trims': '↺ Reset trims',
        'controls.flaps': 'Flaps',
        'controls.flap_pos': 'Flap position',
        'controls.return_heading': 'Return heading',
        'controls.clear': 'Clear',
        // Telemetry
        'telemetry.flight': 'Flight Data',
        'telemetry.heading': 'Heading',
        'telemetry.altitude': 'Altitude',
        'telemetry.airspeed': 'Airspeed',
        'telemetry.bank': 'Bank',
        'telemetry.autoyaw': 'Auto-Yaw',
        'telemetry.raw': 'Raw input',
        'telemetry.smoothed': 'Smoothed',
        'telemetry.output': 'Final output',
        'telemetry.coord': 'Auto coord',
        'telemetry.damper': 'Damper',
        'telemetry.profile': 'Profile',
        'telemetry.aircraft': 'Aircraft',
        'telemetry.no_aircraft': 'No aircraft detected',
    }
};

let currentLang = localStorage.getItem('ayd-lang') || 'fr';

function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('ayd-lang', lang);
    const dict = I18N[lang] || I18N.fr;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.textContent = dict[key];
    });
    // Update language button text on both pages
    document.querySelectorAll('[id^="btn-lang"]').forEach(btn => {
        btn.textContent = lang === 'fr' ? 'EN' : 'FR';
    });
    // Re-apply connection status with new language
    if (typeof currentState !== 'undefined' && currentState.xplane_active !== undefined) {
        setConnected(isConnected, currentState.xplane_active === 'true');
    } else {
        setText('conn-text', dict['status.disconnected']);
        document.querySelectorAll('[id^="status-badge"]').forEach(b => {
            b.textContent = dict['status.offline'];
            b.className = 'status-badge offline';
        });
    }
}

function toggleLanguage() {
    applyLanguage(currentLang === 'fr' ? 'en' : 'fr');
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
    } else {
        document.exitFullscreen().catch(() => {});
    }
}

document.addEventListener('fullscreenchange', () => {
    const icon = document.fullscreenElement ? '⬛' : '⬜';
    document.querySelectorAll('[id^="btn-fullscreen"]').forEach(btn => {
        btn.textContent = icon;
    });
});
const RECONNECT_INTERVAL = 2000; // ms between reconnect attempts

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let currentState = {};
let isConnected = false;
let pollTimer = null;
let commandTimers = {};
let lastPollTime = 0;

// ---------------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------------
const connectionPage = document.getElementById('connection-page');
const appPage = document.getElementById('app-page');
const connDot = document.getElementById('conn-dot');
const connText = document.getElementById('conn-text');
const statusBadge = document.getElementById('status-badge');
const qrContainer = document.getElementById('qr-container');

// Telemetry elements
const telemetryIds = [
    't-heading', 't-altitude', 't-airspeed', 't-bank',
    't-raw', 't-smoothed', 't-output', 't-coord', 't-damper', 't-profile', 't-aircraft'
];

// Slider elements — map server key → { slider, display }
const sliders = {};
document.querySelectorAll('input[type="range"]').forEach(slider => {
    const key = slider.id.replace('s-', '');
    const display = document.getElementById('v-' + key);
    if (display) {
        sliders[key] = { slider, display };
        wrapSliderWithStepButtons(slider, key);
    }
});

// Toggle elements — map server key → checkbox
const toggles = {};
document.querySelectorAll('.toggle-switch input').forEach(cb => {
    const key = cb.id.replace('t-', '');
    toggles[key] = cb;
});

// QR code is now server-generated at /api/qr — loaded via <img> tag in HTML

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------
let isInApp = false;

function enterApp() {
    connectionPage.style.display = 'none';
    appPage.style.display = 'block';
    isInApp = true;
    history.pushState({ page: 'app' }, '');
}

function showConnectionPage() {
    connectionPage.style.display = '';
    appPage.style.display = 'none';
    isInApp = false;
}

// Handle back button — use flag instead of DOM style checks
window.addEventListener('popstate', () => {
    if (isInApp) {
        showConnectionPage();
    }
});

// Push initial state so first back press doesn't close the app
history.replaceState({ page: 'connect' }, '');

// ---------------------------------------------------------------------------
// Tab switching
// ---------------------------------------------------------------------------
function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(
            tabName === 'telemetry' ? 'télémétrie' :
            tabName === 'controls' ? 'contrôles' : 'config'
        )) {
            btn.classList.add('active');
        }
    });

    // Update content
    document.querySelectorAll('.tab-content').forEach(tc => {
        tc.classList.remove('active');
    });
    const target = document.getElementById('tab-' + tabName);
    if (target) target.classList.add('active');
}

// ---------------------------------------------------------------------------
// Polling
// ---------------------------------------------------------------------------
function startPolling() {
    if (pollTimer) return;
    pollLoop();
}

function pollLoop() {
    fetchState().then(() => {
        pollTimer = setTimeout(pollLoop, POLL_INTERVAL);
    }).catch(() => {
        setConnected(false);
        pollTimer = setTimeout(pollLoop, RECONNECT_INTERVAL);
    });
}

async function fetchState() {
    try {
        const resp = await fetch('/api/state', { cache: 'no-store' });
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        currentState = data;
        updateUI(data);
        setConnected(true, data.xplane_active === 'true');
    } catch (e) {
        throw e;
    }
}

// ---------------------------------------------------------------------------
// UI Update
// ---------------------------------------------------------------------------
function updateUI(state) {
    // Telemetry values
    const format = (val, decimals = 2) => {
        const n = parseFloat(val);
        return isNaN(n) ? '---' : n.toFixed(decimals);
    };

    setText('t-heading', format(state.heading));
    setText('t-altitude', format(state.altitude, 0));
    setText('t-airspeed', format(state.airspeed, 1));
    setText('t-bank', format(state.bank_angle));
    setText('t-raw', format(state.raw_input, 3));
    setText('t-smoothed', format(state.smoothed_input, 3));
    setText('t-output', format(state.final_output, 3));
    setText('t-coord', format(state.auto_coord_output, 3));
    setText('t-damper', format(state.damper_output, 3));
    setText('t-profile', state.current_profile || 'Default');
    setText('t-aircraft', state.active_aircraft || 'Aucun avion détecté');
    updateCompass(state.heading);

    // Auto-set return heading when a new aircraft is loaded
    const aircraft = (state.active_aircraft || '').trim();
    if (aircraft && aircraft !== lastAircraft) {
        lastAircraft = aircraft;
        // Reset previous return heading
        returnHeadingCalculated = false;
        returnHeadingFrozen = false;
        const frozenG = document.getElementById('compass-frozen');
        frozenG.style.display = 'none';
        document.getElementById('btn-return-heading').classList.remove('active-return');
        document.getElementById('return-hdg-badge').style.display = 'none';
        document.getElementById('btn-reset-return').style.display = 'none';
        // Auto-click after a short delay to let heading stabilize
        setTimeout(() => { toggleReturnHeading(); }, 1500);
    }

    // Sliders — only update if not currently being dragged
    for (const [key, { slider, display }] of Object.entries(sliders)) {
        if (document.activeElement === slider) continue; // user is dragging
        if (isRecentlyChanged(key)) continue; // command still in flight, don't snap back
        const val = parseFloat(state[key]);
        if (!isNaN(val)) {
            slider.value = val;
            updateSliderDisplay(key, val);
        }
    }

    // Toggles
    for (const [key, cb] of Object.entries(toggles)) {
        if (isRecentlyChanged(key)) continue;
        const val = state[key];
        if (val !== undefined) {
            cb.checked = (val === 'true' || val === '1');
        }
    }
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el && el.textContent !== text) {
        el.textContent = text;
    }
}

function updateSliderDisplay(key, val) {
    const info = sliders[key];
    if (!info) return;
    const step = parseFloat(info.slider.step) || 0.01;
    const decimals = step < 0.1 ? (step < 0.01 ? 3 : 2) : (step < 1 ? 1 : 0);
    info.display.textContent = parseFloat(val).toFixed(decimals);
    updateTrimDiagram(key, val);
    updateCenterDotState(key, val);
}

// ---------------------------------------------------------------------------
// Trim/flap effect diagram — rotates the small aircraft icon to match the slider
// ---------------------------------------------------------------------------
const TRIM_DIAGRAM_CONFIG = {
    elevator_trim: { sign: -1, maxDeg: 35 }, // positive trim = nose up = rotate icon upward
    aileron_trim: { sign: 1, maxDeg: 35 },   // positive trim = roll right
    rudder_trim: { sign: 1, maxDeg: 35 },    // positive trim = yaw right (acts on the tail, not attitude)
    flap_ratio: { sign: 1, maxDeg: 40 },     // 0 = flaps up, 1 = fully deployed
};

function updateTrimDiagram(key, val) {
    const cfg = TRIM_DIAGRAM_CONFIG[key];
    if (!cfg) return;
    const el = document.getElementById('diagram-' + key + '-plane');
    if (!el) return;
    const deg = cfg.sign * parseFloat(val) * cfg.maxDeg;
    el.style.transform = `rotate(${deg}deg)`;
}

// ---------------------------------------------------------------------------
// Heading readout — real aircraft compass, shown in the Trim card header
// ---------------------------------------------------------------------------
let returnHeadingFrozen = false;
let returnHeadingCalculated = false;
let frozenHeading = 0;

let lastAircraft = '';

function toggleReturnHeading() {
    const btn = document.getElementById('btn-return-heading');
    const badge = document.getElementById('return-hdg-badge');
    const frozenG = document.getElementById('compass-frozen');

    if (!returnHeadingCalculated) {
        // First click: calculate and freeze the return heading
        const hdg = parseFloat(currentState.heading);
        if (isNaN(hdg)) return;
        frozenHeading = hdg;
        returnHeadingCalculated = true;

        frozenG.style.transform = `rotate(${frozenHeading}deg)`;
        badge.textContent = ((frozenHeading + 180) % 360).toFixed(0) + '°';
    }

    // Toggle visibility
    returnHeadingFrozen = !returnHeadingFrozen;
    frozenG.style.display = returnHeadingFrozen ? '' : 'none';
    btn.classList.toggle('active-return', returnHeadingFrozen);
    badge.style.display = returnHeadingFrozen ? '' : 'none';
    document.getElementById('btn-reset-return').style.display = returnHeadingFrozen ? '' : 'none';
}

function resetReturnHeading() {
    const btn = document.getElementById('btn-return-heading');
    const badge = document.getElementById('return-hdg-badge');
    const frozenG = document.getElementById('compass-frozen');
    const resetBtn = document.getElementById('btn-reset-return');

    returnHeadingCalculated = false;
    returnHeadingFrozen = false;
    frozenHeading = 0;
    frozenG.style.display = 'none';
    btn.classList.remove('active-return');
    badge.style.display = 'none';
    resetBtn.style.display = 'none';

}

function updateCompass(headingStr) {
    const label = document.getElementById('hdr-heading');
    const rose = document.getElementById('compass-rose');
    const hdg = parseFloat(headingStr);
    if (isNaN(hdg) || !label) return;
    label.textContent = hdg.toFixed(0);
    if (rose) {
        rose.style.transform = `rotate(${-hdg}deg)`;
    }

}

// ---------------------------------------------------------------------------
// Connection status
// ---------------------------------------------------------------------------
function setConnected(connected, xplaneActive) {
    isConnected = connected;
    const dict = I18N[currentLang] || I18N.fr;
    connDot.classList.toggle('connected', connected && xplaneActive);

    let badgeText, badgeClass, connTextStr;
    if (!connected) {
        badgeText = dict['status.offline'];
        badgeClass = 'status-badge offline';
        connTextStr = dict['status.disconnected'];
    } else if (xplaneActive) {
        badgeText = dict['status.live'];
        badgeClass = 'status-badge live';
        connTextStr = dict['status.connected'];
    } else {
        badgeText = dict['status.waiting'];
        badgeClass = 'status-badge waiting';
        connTextStr = dict['status.server_only'];
    }

    connText.textContent = connTextStr;
    // Update both connection-page and app-page badges
    const badges = document.querySelectorAll('[id^="status-badge"]');
    badges.forEach(b => {
        b.textContent = badgeText;
        b.className = badgeClass;
    });
    // Animate enter button based on X-Plane status
    const enterBtn = document.getElementById('btn-enter');
    if (enterBtn) {
        enterBtn.classList.toggle('active-sim', connected && xplaneActive);
        enterBtn.classList.toggle('inactive-sim', !xplaneActive);
    }
}

// ---------------------------------------------------------------------------
// Local-change guard — ignore polled state for a key right after we changed
// it ourselves, until the command has had time to reach the Lua bridge.
// ---------------------------------------------------------------------------
const LOCAL_CHANGE_GUARD_MS = COMMAND_DEBOUNCE + 500;
let recentlyChangedAt = {};

function markRecentlyChanged(key) {
    recentlyChangedAt[key] = Date.now();
}

function isRecentlyChanged(key) {
    const t = recentlyChangedAt[key];
    return t !== undefined && (Date.now() - t) < LOCAL_CHANGE_GUARD_MS;
}

// ---------------------------------------------------------------------------
// Command sending
// ---------------------------------------------------------------------------
function sendCommand(key, value) {
    const body = JSON.stringify({ [key]: value });
    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body
    }).catch(e => console.warn('Command failed:', e));
}

function sendCommands(commands) {
    const body = JSON.stringify({ commands });
    fetch('/api/commands', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body
    }).catch(e => console.warn('Commands failed:', e));
}

// ---------------------------------------------------------------------------
// Slider handler with debounce
// ---------------------------------------------------------------------------
function onSliderChange(el) {
    const key = el.id.replace('s-', '');
    const val = parseFloat(el.value);

    updateSliderDisplay(key, val);
    markRecentlyChanged(key);

    // Debounce: wait for user to stop sliding before sending
    if (commandTimers[key]) clearTimeout(commandTimers[key]);
    commandTimers[key] = setTimeout(() => {
        sendCommand(key, val);
        markRecentlyChanged(key);
    }, COMMAND_DEBOUNCE);
}

// ---------------------------------------------------------------------------
// Step buttons (-/+) and center marker next to each slider
// ---------------------------------------------------------------------------
function wrapSliderWithStepButtons(slider, key) {
    const row = document.createElement('div');
    row.className = 'slider-row';
    slider.parentNode.insertBefore(row, slider);

    const minusBtn = document.createElement('button');
    minusBtn.type = 'button';
    minusBtn.className = 'btn step';
    minusBtn.textContent = '−';
    minusBtn.setAttribute('aria-label', 'Diminuer');
    minusBtn.addEventListener('click', () => stepSlider(key, -1));

    const plusBtn = document.createElement('button');
    plusBtn.type = 'button';
    plusBtn.className = 'btn step';
    plusBtn.textContent = '+';
    plusBtn.setAttribute('aria-label', 'Augmenter');
    plusBtn.addEventListener('click', () => stepSlider(key, 1));

    const trackWrap = document.createElement('div');
    trackWrap.className = 'slider-track-wrap';

    const centerDot = document.createElement('button');
    centerDot.type = 'button';
    centerDot.className = 'slider-center-dot';
    centerDot.setAttribute('aria-label', 'Centrer');
    centerDot.title = 'Centrer';
    centerDot.addEventListener('click', () => centerSlider(key));

    sliders[key].centerDot = centerDot;

    trackWrap.appendChild(slider);
    trackWrap.appendChild(centerDot);

    row.appendChild(minusBtn);
    row.appendChild(trackWrap);
    row.appendChild(plusBtn);
}

function stepSlider(key, direction) {
    const info = sliders[key];
    if (!info) return;
    const { slider } = info;
    const min = parseFloat(slider.min);
    const max = parseFloat(slider.max);
    const step = parseFloat(slider.step) || 0.01;
    const decimals = (step.toString().split('.')[1] || '').length;

    let val = parseFloat(slider.value) + direction * step;
    val = Math.min(max, Math.max(min, val));
    val = parseFloat(val.toFixed(decimals));

    slider.value = val;
    onSliderChange(slider);
}

function centerSlider(key) {
    const info = sliders[key];
    if (!info) return;
    const { slider } = info;
    const min = parseFloat(slider.min);
    const max = parseFloat(slider.max);
    const step = parseFloat(slider.step) || 0.01;
    const decimals = (step.toString().split('.')[1] || '').length;

    let val = parseFloat(((min + max) / 2).toFixed(decimals));
    slider.value = val;
    onSliderChange(slider);
    if (info.centerDot) info.centerDot.blur();
}

function updateCenterDotState(key, val) {
    const info = sliders[key];
    if (!info || !info.centerDot) return;
    const min = parseFloat(info.slider.min);
    const max = parseFloat(info.slider.max);
    const step = parseFloat(info.slider.step) || 0.01;
    const mid = (min + max) / 2;
    const atCenter = Math.abs(parseFloat(val) - mid) < step / 2;
    info.centerDot.classList.toggle('at-center', atCenter);
}

// ---------------------------------------------------------------------------
// Toggle handler
// ---------------------------------------------------------------------------
function onToggleChange(el) {
    const key = el.id.replace('t-', '');
    markRecentlyChanged(key);
    sendCommand(key, el.checked ? 'true' : 'false');
}

// ---------------------------------------------------------------------------
// Button actions
// ---------------------------------------------------------------------------
function resetTrims() {
    sendCommands([
        { action: 'set', key: 'elevator_trim', value: '0' },
        { action: 'set', key: 'aileron_trim', value: '0' },
        { action: 'set', key: 'rudder_trim', value: '0' }
    ]);

    // Update local UI immediately
    ['elevator_trim', 'aileron_trim', 'rudder_trim'].forEach(key => {
        markRecentlyChanged(key);
        if (sliders[key]) {
            sliders[key].slider.value = 0;
            updateSliderDisplay(key, 0);
        }
    });
}

function setFlaps(value) {
    markRecentlyChanged('flap_ratio');
    sendCommand('flap_ratio', value.toString());
    if (sliders.flap_ratio) {
        sliders.flap_ratio.slider.value = value;
        updateSliderDisplay('flap_ratio', value);
    }
}

// ---------------------------------------------------------------------------
// Initialize
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    // QR code is loaded server-side via <img src="/api/qr">

    // Apply saved language to both pages
    applyLanguage(currentLang);

    // Start polling immediately (works on connection page too)
    startPolling();

    // If opened directly (not from connection page), go to app
    if (window.location.search.includes('autoconnect')) {
        enterApp();
    }
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    if (pollTimer) clearTimeout(pollTimer);
    for (const t of Object.values(commandTimers)) {
        clearTimeout(t);
    }
});

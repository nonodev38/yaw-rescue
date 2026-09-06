/**
 * AUTO-YAW DECK — UI
 * DOM references, slider/toggle element maps, live UI updates, page
 * navigation, tab switching and the connection status badge.
 */

// ---------------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------------
const connectionPage = document.getElementById('connection-page');
const appPage = document.getElementById('app-page');
const connDot = document.getElementById('conn-dot');
const connText = document.getElementById('conn-text');

// Slider elements — map server key → { slider, display }
const sliders = {};
const toggles = {};

function buildSliderMaps() {
    document.querySelectorAll('input[type="range"]').forEach(slider => {
        const key = slider.id.replace('s-', '');
        const display = document.getElementById('v-' + key);
        if (display) {
            sliders[key] = { slider, display };
            wrapSliderWithStepButtons(slider, key);
        }
    });

    // Toggle elements — map server key → checkbox
    document.querySelectorAll('.toggle-switch input').forEach(cb => {
        const key = cb.id.replace('t-', '');
        toggles[key] = cb;
    });
}

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
    // Update buttons (matched via data-tab so it works in any language)
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
    });

    // Update content
    document.querySelectorAll('.tab-content').forEach(tc => {
        tc.classList.remove('active');
    });
    const target = document.getElementById('tab-' + tabName);
    if (target) target.classList.add('active');

    // Remember the selected tab so it is restored on the next visit
    try {
        localStorage.setItem('ayd-tab', tabName);
    } catch (e) { /* storage unavailable */ }
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
        if (isNaN(val)) continue;
        const current = parseFloat(slider.value);
        // Only update if value actually differs (avoid micro-flicker from float rounding)
        if (Math.abs(val - current) > 0.001) {
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

    // Flap retract alert — flash the Volets section when it's time to
    // raise the flaps (airspeed at/beyond Vfe with flaps extended)
    const flapCard = document.getElementById('card-flaps');
    if (flapCard) {
        flapCard.classList.toggle('flap-alert', state.flap_alert === 'true');
    }

    // Flight vitals around the compass (gear, RPM/thrust, FPM, AOA)
    updateVitals(state);
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el && el.textContent !== text) {
        el.textContent = text;
    }
}

// ---------------------------------------------------------------------------
// Collapsible cards — tap the header to fold/unfold the section
// ---------------------------------------------------------------------------
function toggleCollapse(cardId) {
    const card = document.getElementById(cardId);
    if (!card) return;
    const collapsed = card.classList.toggle('collapsed');
    try {
        localStorage.setItem('ayd-collapsed-' + cardId, collapsed ? '1' : '0');
    } catch (e) { /* storage unavailable */ }
}

function initCollapsibleCards() {
    document.querySelectorAll('.card.collapsible').forEach(card => {
        let collapsed = false;
        try {
            collapsed = localStorage.getItem('ayd-collapsed-' + card.id) === '1';
        } catch (e) { /* storage unavailable */ }
        if (collapsed) card.classList.add('collapsed');
    });
}

// ---------------------------------------------------------------------------
// Flap position badge — shown in the Volets card header, color-coded by
// deployment (0% green, partial orange, fully deployed red)
// ---------------------------------------------------------------------------
function updateFlapBadge(ratio) {
    const badge = document.getElementById('flap-pos-badge');
    if (!badge) return;
    const r = parseFloat(ratio) || 0;
    badge.textContent = Math.round(r * 100) + '%';
    let cls = 'ok';
    if (r > 0.67) cls = 'max';
    else if (r > 0.34) cls = 'hot';
    else if (r > 0) cls = 'warn';
    badge.className = 'flap-pos-badge ' + cls;
}

// ---------------------------------------------------------------------------
// Flap preset buttons — highlight the preset closest to the current flap
// position (0% / 1/3 / 2/3 / Full)
// ---------------------------------------------------------------------------
function updateFlapPresets(ratio) {
    const r = parseFloat(ratio) || 0;
    const buttons = document.querySelectorAll('#card-flaps [data-flap-preset]');
    let best = null;
    let bestDist = Infinity;
    buttons.forEach(btn => {
        const preset = parseFloat(btn.getAttribute('data-flap-preset')) || 0;
        const dist = Math.abs(r - preset);
        if (dist < bestDist) {
            bestDist = dist;
            best = btn;
        }
    });
    buttons.forEach(btn => {
        btn.classList.toggle('active', btn === best);
    });
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
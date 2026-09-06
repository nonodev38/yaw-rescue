/**
 * AUTO-YAW DECK — Sliders
 * Widgets around each range input: −/+ step buttons, center marker,
 * debounced command sending, and the trim/flap effect diagrams that rotate
 * a small aircraft icon to match the slider value.
 */

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

function updateSliderDisplay(key, val) {
    const info = sliders[key];
    if (!info) return;
    const step = parseFloat(info.slider.step) || 0.01;
    const decimals = step < 0.1 ? (step < 0.01 ? 3 : 2) : (step < 1 ? 1 : 0);
    info.display.textContent = parseFloat(val).toFixed(decimals);
    updateTrimDiagram(key, val);
    updateCenterDotState(key, val);
    // Keep the Volets header badge + preset buttons in sync
    if (key === 'flap_ratio') {
        const r = parseFloat(val) || 0;
        updateFlapBadge(r);
        updateFlapPresets(r);
    }
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
/**
 * AUTO-YAW DECK — Flight vitals
 * Landing gear states (per gear), engine RPM/throttle, vertical speed (FPM)
 * and angle of attack (AOA), displayed around the compass. Values are
 * color-coded interactively, and the gear strip flashes when a landing
 * config alert is active (gear not down at low altitude, or flap alert).
 */

const GEAR_ALERT_ALT_FT = 1000; // flash the gear strip below this altitude

function vitalClass(value, warnAt, dangerAt) {
    if (dangerAt !== undefined && value >= dangerAt) return 'vital-danger';
    if (warnAt !== undefined && value >= warnAt) return 'vital-warn';
    return 'vital-ok';
}

function setVital(id, text, cls) {
    const el = document.getElementById(id);
    if (!el) return;
    if (el.textContent !== text) el.textContent = text;
    if (cls) el.className = 'side-value ' + cls;
}

function updateGearCell(cellId, valueId, ratio) {
    const cell = document.getElementById(cellId);
    const val = document.getElementById(valueId);
    if (!cell || !val) return;
    const r = parseFloat(ratio) || 0;
    const down = r >= 0.9;
    const up = r <= 0.1;
    const text = down ? 'DN' : (up ? 'UP' : 'MID');
    if (val.textContent !== text) val.textContent = text;
    const cls = down ? 'down' : (up ? 'up' : 'mid');
    cell.className = 'gear-cell ' + cls;
}

function updateVitals(state) {
    // Landing gear — one cell per gear
    updateGearCell('gear-nose', 'v-gear-nose', state.gear_nose);
    updateGearCell('gear-left', 'v-gear-left', state.gear_left);
    updateGearCell('gear-right', 'v-gear-right', state.gear_right);

    // RPM — engine running = green, off = muted
    const rpm = parseFloat(state.rpm) || 0;
    setVital('v-rpm',
        rpm > 0 ? String(Math.round(rpm)) : '---',
        rpm > 0 ? 'vital-ok' : 'vital-off');

    // Throttle — 0 idle, high thrust = warning/danger
    const thr = (parseFloat(state.throttle) || 0) * 100;
    setVital('v-throttle',
        thr > 0 ? Math.round(thr) + '%' : '---',
        thr > 0 ? vitalClass(thr, 70, 90) : 'vital-off');

    // Vertical speed (FPM) — smooth = green, fast descent = orange/red
    const vspd = Math.round(parseFloat(state.vspd_fpm) || 0);
    const fpmCls = vspd < -1000 ? 'vital-danger'
        : (vspd < -400 ? 'vital-warn' : 'vital-ok');
    setVital('v-fpm', (vspd > 0 ? '+' : '') + vspd, fpmCls);

    // Angle of attack (deg) — low = green, high (stall approach) = red
    const aoa = parseFloat(state.alpha_deg) || 0;
    setVital('v-aoa', aoa.toFixed(1) + '°', vitalClass(aoa, 12, 16));

    // Landing config alert — flash the strip when gear isn't fully down
    // at low altitude, or when the flap retract alert is active
    const strip = document.getElementById('gear-strip');
    if (strip) {
        const anyGearUp = (parseFloat(state.gear_nose) || 0) < 0.9
            || (parseFloat(state.gear_left) || 0) < 0.9
            || (parseFloat(state.gear_right) || 0) < 0.9;
        const lowAlt = (parseFloat(state.altitude) || 0) < GEAR_ALERT_ALT_FT;
        const alert = (anyGearUp && lowAlt) || state.flap_alert === 'true';
        strip.classList.toggle('alert', alert);
    }
}
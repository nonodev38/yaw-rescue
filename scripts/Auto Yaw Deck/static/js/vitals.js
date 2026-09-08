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

function updateGearCellBoth(ratio, prefix) {
    updateGearCell(prefix + 'gear-nose', prefix + 'tv-gear-nose', ratio);
}

function updateVitals(state) {
    try {
        // Landing gear — Controls tab
        updateGearCell('gear-nose', 'v-gear-nose', state.gear_nose);
    updateGearCell('gear-left', 'v-gear-left', state.gear_left);
    updateGearCell('gear-right', 'v-gear-right', state.gear_right);

    // Landing gear — Telemetry tab
    updateGearCell('t-gear-nose', 'tv-gear-nose', state.gear_nose);
    updateGearCell('t-gear-left', 'tv-gear-left', state.gear_left);
    updateGearCell('t-gear-right', 'tv-gear-right', state.gear_right);

    // RPM — engine running = green, off = muted
    const rpm = parseFloat(state.rpm) || 0;
    const rpmText = rpm > 0 ? String(Math.round(rpm)) : '---';
    const rpmCls = rpm > 0 ? 'vital-ok' : 'vital-off';
    setVital('v-rpm', rpmText, rpmCls);
    setVital('tv-rpm', rpmText, rpmCls);

    // Throttle — 0 idle, high thrust = warning/danger
    const thr = (parseFloat(state.throttle) || 0) * 100;
    const thrText = thr > 0 ? Math.round(thr) + '%' : '---';
    const thrCls = thr > 0 ? vitalClass(thr, 70, 90) : 'vital-off';
    setVital('v-throttle', thrText, thrCls);
    setVital('tv-throttle', thrText, thrCls);

    // Vertical speed (FPM) — smooth = green, fast descent = orange/red
    const vspd = Math.round(parseFloat(state.vspd_fpm) || 0);
    const fpmCls = vspd < -1000 ? 'vital-danger'
        : (vspd < -400 ? 'vital-warn' : 'vital-ok');
    const fpmText = (vspd > 0 ? '+' : '') + vspd;
    setVital('v-fpm', fpmText, fpmCls);
    setVital('tv-fpm', fpmText, fpmCls);

    // Angle of attack (deg) — low = green, high (stall approach) = red
    const aoa = parseFloat(state.alpha_deg) || 0;
    const aoaText = aoa.toFixed(1) + '°';
    const aoaCls = vitalClass(aoa, 12, 16);
    setVital('v-aoa', aoaText, aoaCls);
    setVital('tv-aoa', aoaText, aoaCls);

    // Yaw rate (deg/s) — telemetry only, no controls-side counterpart
    const yawRate = parseFloat(state.yaw_rate) || 0;
    const yawRateText = yawRate.toFixed(1) + '°/s';
    const yawRateCls = yawRate > 0 ? vitalClass(Math.abs(yawRate), 30, 60) : 'vital-off';
    setVital('tv-yaw_rate', yawRateText, yawRateCls);

    // Flap VFE (max speed with flaps extended, knots) — telemetry only
    const flapVfe = parseFloat(state.flap_vfe) || 0;
    const flapVfeText = flapVfe > 0 ? String(Math.round(flapVfe)) + ' KTS' : '---';
    const flapVfeCls = flapVfe > 0 ? 'vital-ok' : 'vital-off';
    setVital('tv-flap_vfe', flapVfeText, flapVfeCls);

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
    // Also flash the telemetry gear strip
    const tStrip = document.getElementById('t-gear-strip');
    if (tStrip) {
        const anyGearUp = (parseFloat(state.gear_nose) || 0) < 0.9
            || (parseFloat(state.gear_left) || 0) < 0.9
            || (parseFloat(state.gear_right) || 0) < 0.9;
        const lowAlt = (parseFloat(state.altitude) || 0) < GEAR_ALERT_ALT_FT;
        const alert = (anyGearUp && lowAlt) || state.flap_alert === 'true';
        tStrip.classList.toggle('alert', alert);
    }
    } catch (e) {
        console.error('[updateVitals] error:', e);
    }
}
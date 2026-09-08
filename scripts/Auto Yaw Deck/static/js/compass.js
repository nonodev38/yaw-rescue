/**
 * AUTO-YAW DECK — Compass & return heading
 * Real aircraft compass shown in the Trim card, plus the "return heading"
 * feature that freezes the current heading and displays a yellow arrow at
 * the reciprocal (180° opposite) direction.
 */

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
    const hdg = parseFloat(headingStr);
    if (isNaN(hdg)) return;

    // Update Controls tab compass
    const label = document.getElementById('hdr-heading');
    const rose = document.getElementById('compass-rose');
    if (label) label.textContent = hdg.toFixed(0);
    if (rose) rose.style.transform = `rotate(${-hdg}deg)`;    // Update Telemetry tab compass
    const tLabel = document.getElementById('t-hdr-heading');
    const tRose = document.getElementById('t-compass-rose');
    if (tLabel) tLabel.textContent = hdg.toFixed(0);
    if (tRose) tRose.style.transform = `rotate(${-hdg}deg)`;
}

// ---------------------------------------------------------------------------
// Compass rose graduation (P4.1) — the tick marks used to be hard-coded in
// index.html (2 × 24 <line>). They are now generated here at startup so the
// HTML only keeps the fixed parts. Geometry is radial around (50,50):
//   major tick every 30°  : r 38 → 46, stroke 1.2 / opacity 0.7
//   minor tick every 15°  : r 38 → 42.5, stroke 0.8 / opacity 0.4
// Same rose layout as before; guarded so it runs once per rose.
// ---------------------------------------------------------------------------
function _compassTickPoint(deg, r) {
    const rad = deg * Math.PI / 180;
    return {
        x: +(50 + r * Math.sin(rad)).toFixed(1),
        y: +(50 - r * Math.cos(rad)).toFixed(1),
    };
}

function _compassTickLine(deg, rIn, rOut) {
    const SVG_NS = 'http://www.w3.org/2000/svg';
    const from = _compassTickPoint(deg, rIn);
    const to = _compassTickPoint(deg, rOut);
    const line = document.createElementNS(SVG_NS, 'line');
    line.setAttribute('x1', from.x);
    line.setAttribute('y1', from.y);
    line.setAttribute('x2', to.x);
    line.setAttribute('y2', to.y);
    return line;
}

function buildCompassRose(roseId) {
    const rose = document.getElementById(roseId);
    if (!rose || rose.getAttribute('data-ticks') === 'built') return;
    rose.setAttribute('data-ticks', 'built');

    const SVG_NS = 'http://www.w3.org/2000/svg';

    // Major ticks every 30° (0°, 30°, …, 330°)
    const major = document.createElementNS(SVG_NS, 'g');
    major.setAttribute('stroke', 'var(--text-muted)');
    major.setAttribute('stroke-width', '1.2');
    major.setAttribute('opacity', '0.7');
    for (let deg = 0; deg < 360; deg += 30) {
        major.appendChild(_compassTickLine(deg, 38, 46));
    }

    // Minor ticks every 15° (15°, 45°, …, 345°) — shorter than the majors
    const minor = document.createElementNS(SVG_NS, 'g');
    minor.setAttribute('stroke', 'var(--text-muted)');
    minor.setAttribute('stroke-width', '0.8');
    minor.setAttribute('opacity', '0.4');
    for (let deg = 15; deg < 360; deg += 30) {
        minor.appendChild(_compassTickLine(deg, 38, 42.5));
    }

    // Insert ticks first so the cardinal labels / return arrow stay on top
    rose.insertBefore(major, rose.firstChild);
    rose.insertBefore(minor, rose.firstChild);
}

function initCompassTicks() {
    buildCompassRose('compass-rose');
    buildCompassRose('t-compass-rose');
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCompassTicks);
} else {
    initCompassTicks();
}

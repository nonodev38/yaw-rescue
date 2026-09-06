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
    const label = document.getElementById('hdr-heading');
    const rose = document.getElementById('compass-rose');
    const hdg = parseFloat(headingStr);
    if (isNaN(hdg) || !label) return;
    label.textContent = hdg.toFixed(0);
    if (rose) {
        rose.style.transform = `rotate(${-hdg}deg)`;
    }

}
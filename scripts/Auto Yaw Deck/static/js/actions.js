/**
 * AUTO-YAW DECK — Button actions
 * High-level actions triggered from the web interface (trim reset, flaps).
 */

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
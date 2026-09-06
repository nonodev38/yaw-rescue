/**
 * AUTO-YAW DECK — Bootstrap
 * Application initialization and cleanup. Loaded last, after all modules.
 */

document.addEventListener('DOMContentLoaded', () => {
    // QR code is loaded server-side via <img src="/api/qr">

    // Verify telemetry DOM elements are present
    verifyTelemetryDOM();

    // Apply saved language to both pages
    applyLanguage(currentLang);

    // Prefer the server-saved language (survives IP changes / other devices)
    fetchServerLang().then(serverLang => {
        if (serverLang && serverLang !== currentLang) {
            applyLanguage(serverLang);
        }
    });

    // Build slider/toggle element maps (after language, before polling)
    buildSliderMaps();

    // Restore collapsed state of collapsible cards (flaps section)
    initCollapsibleCards();

    // Restore the last selected tab (config / controls / telemetry)
    const savedTab = localStorage.getItem('ayd-tab');
    if (['config', 'controls', 'telemetry'].includes(savedTab)) {
        switchTab(savedTab);
    }

    // Initial flap indicators (badge + preset highlight) from the slider
    if (sliders.flap_ratio) {
        const r = parseFloat(sliders.flap_ratio.slider.value) || 0;
        updateFlapBadge(r);
        updateFlapPresets(r);
    }

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
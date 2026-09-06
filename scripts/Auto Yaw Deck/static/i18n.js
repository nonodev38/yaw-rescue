/**
 * AUTO-YAW DECK — Internationalization (FR / EN)
 * Translation dictionary plus language management. The preference is saved
 * in localStorage and server-side (data/prefs.json) so it survives X-Plane
 * restarts, IP changes, and is shared by every device.
 */

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
        'telemetry.autoyaw': 'Yaw Rescue',
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
        'telemetry.autoyaw': 'Yaw Rescue',
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

// ---------------------------------------------------------------------------
// Language state
// ---------------------------------------------------------------------------
let currentLang = localStorage.getItem('ayd-lang') || 'fr';

// Language preference is also saved server-side (data/prefs.json) so it
// survives X-Plane restarts, IP changes and is shared by every device.
function fetchServerLang() {
    return fetch('/api/prefs', { cache: 'no-store' })
        .then(r => r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))
        .then(d => (d && (d.lang === 'fr' || d.lang === 'en')) ? d.lang : Promise.reject(new Error('no lang')))
        .catch(() => null);
}

function saveServerLang(lang) {
    fetch('/api/prefs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lang })
    }).catch(e => console.warn('Could not save language:', e));
}

function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('ayd-lang', lang);
    saveServerLang(lang);
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

// ---------------------------------------------------------------------------
// Fullscreen toggle
// ---------------------------------------------------------------------------
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
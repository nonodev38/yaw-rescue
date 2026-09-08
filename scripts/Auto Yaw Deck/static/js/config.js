/**
 * AUTO-YAW DECK — Configuration
 * Tunable constants shared by the other client-side modules.
 */

// ms between state polls
const POLL_INTERVAL = 150;

// ms before sending slider changes (debounce)
const COMMAND_DEBOUNCE = 200;

// ---------------------------------------------------------------------------
// P4.2 — Onglet Config généré par données.
// Chaque carte = { title, icon, info } + une liste de contrôles :
//   slider : { type:'slider', name, fallback, key, min, max, step, value, display }
//   toggle : { type:'toggle', name, fallback, key }
// Les IDs s-*/v-*/t-* restent identiques à l'ancien HTML : buildSliderMaps(),
// updateUI() et les handlers inline fonctionnent sans changement.
// ---------------------------------------------------------------------------
const CONFIG_CARDS = [
    {
        title: 'config.smoothing', titleFallback: 'Lissage du signal', icon: '🔧', info: 'config.smoothing',
        controls: [
            { type: 'slider', name: 'config.smoothing_factor', fallback: 'Facteur de lissage',
              key: 'smoothing_factor', min: 0.01, max: 0.50, step: 0.01, value: 0.15, display: '0.15' },
        ],
    },
    {
        title: 'config.noise', titleFallback: 'Filtre anti-bruit', icon: '🔇', info: 'config.noise',
        controls: [
            { type: 'slider', name: 'config.noise_threshold', fallback: 'Seuil anti-bruit',
              key: 'noise_filter', min: 0, max: 0.30, step: 0.01, value: 0.05, display: '0.05' },
        ],
    },
    {
        title: 'config.deadzone', titleFallback: 'Zone morte', icon: '⭕', info: 'config.deadzone',
        controls: [
            { type: 'slider', name: 'config.deadzone_size', fallback: 'Taille zone morte',
              key: 'deadzone_size', min: 0, max: 0.20, step: 0.01, value: 0.03, display: '0.03' },
        ],
    },
    {
        title: 'config.autocoord', titleFallback: 'Auto-Coordination', icon: '🔄', info: 'config.autocoord',
        controls: [
            { type: 'slider', name: 'config.coord_gain', fallback: 'Gain de coordination',
              key: 'auto_coord_gain', min: 0, max: 1, step: 0.01, value: 0.40, display: '0.40' },
            { type: 'slider', name: 'config.bank_limit', fallback: 'Limite de bank (DEG)',
              key: 'coord_bank_limit', min: 5, max: 60, step: 1, value: 35, display: '35.0' },
        ],
    },
    {
        title: 'config.damper', titleFallback: 'Yaw Damper', icon: '🛑', info: 'config.damper',
        controls: [
            { type: 'slider', name: 'config.damper_gain', fallback: 'Gain du damper',
              key: 'damper_gain', min: 0, max: 1, step: 0.01, value: 0.30, display: '0.30' },
            { type: 'slider', name: 'config.sensitivity', fallback: 'Sensibilité',
              key: 'damper_sensitivity', min: 0.5, max: 5, step: 0.1, value: 2.0, display: '2.00' },
        ],
    },
    {
        title: 'config.options', titleFallback: 'Options', icon: '⚡', info: 'config.options',
        controls: [
            { type: 'toggle', name: 'config.enable', fallback: 'Activer le plugin', key: 'enabled' },
            { type: 'toggle', name: 'config.smoothing_on', fallback: 'Lissage', key: 'smoothing_enabled' },
            { type: 'toggle', name: 'config.deadzone_on', fallback: 'Zone morte', key: 'deadzone_enabled' },
            { type: 'toggle', name: 'config.autocoord_on', fallback: 'Auto-coordination', key: 'auto_coord_enabled' },
            { type: 'toggle', name: 'config.damper_on', fallback: 'Yaw damper', key: 'yaw_damper_enabled' },
        ],
    },
];

function _configInfoBtn(infoKey) {
    return '<button class="info-btn" onclick="openInfo(\'' + infoKey + '\')">' +
           '<svg width="12" height="12" aria-hidden="true"><use href="#icon-info"/></svg></button>';
}

function _configSliderHtml(ctl) {
    return '<div class="control-group">' +
                '<div class="control-label">' +
                    '<span class="name" data-i18n="' + ctl.name + '">' + ctl.fallback + '</span>' +
                    '<span class="val" id="v-' + ctl.key + '">' + ctl.display + '</span>' +
                '</div>' +
                '<input type="range" min="' + ctl.min + '" max="' + ctl.max + '" step="' + ctl.step + '" value="' + ctl.value + '"' +
                       ' id="s-' + ctl.key + '" oninput="onSliderChange(this)">' +
            '</div>';
}

function _configToggleHtml(ctl) {
    return '<div class="toggle-row">' +
                '<span class="name" data-i18n="' + ctl.name + '">' + ctl.fallback + '</span>' +
                '<label class="toggle-switch">' +
                    '<input type="checkbox" id="t-' + ctl.key + '" checked onchange="onToggleChange(this)">' +
                    '<span class="slider"></span>' +
                '</label>' +
            '</div>';
}

function configCardHtml(card) {
    const body = card.controls
        .map(ctl => ctl.type === 'toggle' ? _configToggleHtml(ctl) : _configSliderHtml(ctl))
        .join('');
    return '<div class="card">' +
                '<div class="card-header">' +
                    '<span class="icon">' + card.icon + '</span> ' +
                    '<span data-i18n="' + card.title + '">' + card.titleFallback + '</span>' +
                    _configInfoBtn(card.info) +
                '</div>' +
                '<div class="card-body">' + body + '</div>' +
            '</div>';
}

function renderConfigCards() {
    const container = document.getElementById('tab-config');
    if (!container || container.getAttribute('data-rendered') === '1') return;
    container.setAttribute('data-rendered', '1');
    container.innerHTML = CONFIG_CARDS.map(configCardHtml).join('\n');
}

// Rend les cartes dès que le DOM est prêt (avant buildSliderMaps() de main.js,
// car les scripts sont chargés dans l'ordre : config.js < … < main.js).
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderConfigCards);
} else {
    renderConfigCards();
}

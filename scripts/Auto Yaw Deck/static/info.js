/**
 * AUTO-YAW DECK — Info panels for Config tab
 * Shows detailed explanations for each config section in a modal.
 */

const INFO_DATA = {
    fr: {
        'config.smoothing': {
            title: '🔧 Lissage du signal',
            sections: [
                {
                    heading: 'À quoi sert ?',
                    text: 'Le lissage réduit les variations brutales de l\'entrée joystick. Il applique un filtre exponentiel (moyenne mobile) qui adoucit les mouvements sans ajouter de retard perceptible.'
                },
                {
                    heading: 'Facteur de lissage',
                    text: 'Valeur entre 0.01 et 0.50.\n• Plus la valeur est basse, plus le lissage est fort (réponse plus lente).\n• Plus la valeur est haute, plus la réponse est directe (mais plus de bruit).\n• Recommandé : 0.10 – 0.20 pour la plupart des joysticks.'
                },
                {
                    heading: 'Quand l\'utiliser ?',
                    text: 'Activez le lissage si vous remarquez des à-coups dans le yaw alors que vos mouvements sont fluides. Désactivez-le si vous avez besoin d\'une réponse ultra-réactive (simulation de combat).'
                }
            ]
        },
        'config.noise': {
            title: '🔇 Filtre anti-bruit',
            sections: [
                {
                    heading: 'À quoi sert ?',
                    text: 'Ce filtre détecte les oscillations rapides du joystick — un phénomène courant avec les potentiomètres usés ou de mauvaise qualité. Quand le capteur envoie des sauts de valeur trop brutaux (physiquement impossibles), le filtre ignore ces pics.'
                },
                {
                    heading: 'Seuil anti-bruit',
                    text: 'Valeur entre 0.00 et 0.30.\n• 0.00 = filtre désactivé.\n• 0.05 = seuil par défaut (bon compromis).\n• 0.10 – 0.15 = filtrage agressif pour joysticks très bruyants.\n• Plus le seuil est bas, plus le filtre est sensible.'
                },
                {
                    heading: 'Comment ça marche ?',
                    text: 'À chaque image, le filtre compare la valeur brute actuelle à la précédente. Si la différence dépasse le seuil, la valeur est rejetée et la dernière valeur lissée est conservée. Cela élimine le jitter sans affecter les mouvements réels.'
                }
            ]
        },
        'config.deadzone': {
            title: '⭕ Zone morte',
            sections: [
                {
                    heading: 'À quoi sert ?',
                    text: 'La zone morte ignore les petits déplacements du joystick autour du centre. Cela compense le jeu mécanique (\"play\") des potentiomètres et empêche les mouvements parasites quand le yaw est au repos.'
                },
                {
                    heading: 'Taille zone morte',
                    text: 'Valeur entre 0.00 et 0.20.\n• 0.00 = aucune zone morte.\n• 0.03 = valeur par défaut.\n• 0.05 – 0.10 = pour joysticks avec beaucoup de jeu.\n• La zone morte est progressivement retirée en sortant du centre.'
                },
                {
                    heading: 'Conseil',
                    text: 'Utilisez la zone morte en complément du lissage et du filtre anti-bruit pour un signal propre. Si votre joystick est de bonne qualité, une petite zone morte (0.02) suffit.'
                }
            ]
        },
        'config.autocoord': {
            title: '🔄 Auto-Coordination',
            sections: [
                {
                    heading: 'À quoi sert ?',
                    text: 'L\'auto-coordination applique automatiquement uneCorrection de direction proportionnelle à l\'angle de banque. Quand l\'avion s\'incline, la direction est naturellement déviée — ce filtre compense cet effet, comme le ferait un pilote expérimenté.'
                },
                {
                    heading: 'Gain de coordination',
                    text: 'Valeur entre 0.00 et 1.00.\n• 0.00 = désactivé.\n• 0.40 = valeur par défaut.\n• 0.60 – 0.80 = coordination forte (utile pour les avions légers).\n• Le gain détermine l\'intensité de la correction.'
                },
                {
                    heading: 'Limite de bank',
                    text: 'Angle de bank maximum (en degrés) au-delà duquel la correction est plafonnée. Par défaut 35°. Empêche les corrections excessives en virage serré.'
                }
            ]
        },
        'config.damper': {
            title: '🛑 Yaw Damper',
            sections: [
                {
                    heading: 'À quoi sert ?',
                    text: 'Le yaw damper réduit les oscillations de lacet (\"Dutch roll\") en appliquant une Correction proportionnelle à la vitesse de rotation du yaw. C\'est le même principe que les dampers des avions de ligne.'
                },
                {
                    heading: 'Gain du damper',
                    text: 'Valeur entre 0.00 et 1.00.\n• 0.00 = désactivé.\n• 0.30 = valeur par défaut.\n• 0.50 – 0.70 = damper fort (utile pour les avions à stabilité latérale faible).'
                },
                {
                    heading: 'Sensibilité',
                    text: 'Valeur entre 0.5 et 5.0.\n• Contrôle la réactivité du filtre à la vitesse de rotation.\n• Plus la sensibilité est haute, plus le damper réagit vite aux changements.\n• 2.0 = valeur par défaut.'
                }
            ]
        },
        'config.options': {
            title: '⚡ Options',
            sections: [
                {
                    heading: 'Activer le plugin',
                    text: 'Active ou désactive l\'override du joystick. Quand désactivé, le yaw revient au contrôle direct du joystick sans aucun traitement.'
                },
                {
                    heading: 'Lissage',
                    text: 'Active ou désactive le filtre de lissage du signal d\'entrée.'
                },
                {
                    heading: 'Zone morte',
                    text: 'Active ou désactive la zone morte autour du centre du joystick.'
                },
                {
                    heading: 'Auto-coordination',
                    text: 'Active ou désactive la correction automatique de direction en virage.'
                },
                {
                    heading: 'Yaw damper',
                    text: 'Active ou désactive l\'amortisseur de lacet.'
                }
            ]
        }
    },
    en: {
        'config.smoothing': {
            title: '🔧 Signal Smoothing',
            sections: [
                {
                    heading: 'What does it do?',
                    text: 'Smoothing reduces harsh variations from the joystick input. It applies an exponential filter (moving average) that softens movements without adding noticeable delay.'
                },
                {
                    heading: 'Smoothing factor',
                    text: 'Value between 0.01 and 0.50.\n• Lower = stronger smoothing (slower response).\n• Higher = more direct response (but more noise).\n• Recommended: 0.10 – 0.20 for most joysticks.'
                },
                {
                    heading: 'When to use?',
                    text: 'Enable smoothing if you notice yaw jitters despite smooth stick movements. Disable it if you need ultra-responsive input (combat simulation).'
                }
            ]
        },
        'config.noise': {
            title: '🔇 Noise Filter',
            sections: [
                {
                    heading: 'What does it do?',
                    text: 'This filter detects rapid joystick oscillations — a common issue with worn or low-quality potentiometers. When the sensor sends impossibly fast value jumps, the filter rejects those spikes.'
                },
                {
                    heading: 'Noise threshold',
                    text: 'Value between 0.00 and 0.30.\n• 0.00 = filter disabled.\n• 0.05 = default (good balance).\n• 0.10 – 0.15 = aggressive filtering for very noisy joysticks.\n• Lower threshold = more sensitive filter.'
                },
                {
                    heading: 'How it works',
                    text: 'Each frame, the filter compares the current raw value to the previous one. If the delta exceeds the threshold, the value is rejected and the last smoothed value is kept. This eliminates jitter without affecting real movements.'
                }
            ]
        },
        'config.deadzone': {
            title: '⭕ Dead Zone',
            sections: [
                {
                    heading: 'What does it do?',
                    text: 'The dead zone ignores small joystick movements around the center. This compensates for mechanical play in potentiometers and prevents phantom input when the yaw is at rest.'
                },
                {
                    heading: 'Dead zone size',
                    text: 'Value between 0.00 and 0.20.\n• 0.00 = no dead zone.\n• 0.03 = default.\n• 0.05 – 0.10 = for joysticks with significant play.\n• The dead zone is progressively removed as you move away from center.'
                },
                {
                    heading: 'Tip',
                    text: 'Use the dead zone alongside smoothing and the noise filter for a clean signal. If your joystick is high quality, a small dead zone (0.02) is sufficient.'
                }
            ]
        },
        'config.autocoord': {
            title: '🔄 Auto-Coordination',
            sections: [
                {
                    heading: 'What does it do?',
                    text: 'Auto-coordination automatically applies a yaw correction proportional to the bank angle. When the aircraft banks, yaw is naturally induced — this filter compensates for it, just like an experienced pilot would.'
                },
                {
                    heading: 'Coordination gain',
                    text: 'Value between 0.00 and 1.00.\n• 0.00 = disabled.\n• 0.40 = default.\n• 0.60 – 0.80 = strong coordination (useful for light aircraft).\n• The gain determines the correction intensity.'
                },
                {
                    heading: 'Bank limit',
                    text: 'Maximum bank angle (in degrees) beyond which the correction is capped. Default is 35°. Prevents excessive corrections in tight turns.'
                }
            ]
        },
        'config.damper': {
            title: '🛑 Yaw Damper',
            sections: [
                {
                    heading: 'What does it do?',
                    text: 'The yaw damper reduces yaw oscillations (\"Dutch roll\") by applying a correction proportional to the yaw rotation rate. This is the same principle used in airliner autopilots.'
                },
                {
                    heading: 'Damper gain',
                    text: 'Value between 0.00 and 1.00.\n• 0.00 = disabled.\n• 0.30 = default.\n• 0.50 – 0.70 = strong damper (useful for aircraft with low lateral stability).'
                },
                {
                    heading: 'Sensitivity',
                    text: 'Value between 0.5 and 5.0.\n• Controls how responsive the filter is to yaw rotation speed.\n• Higher sensitivity = damper reacts faster to changes.\n• 2.0 = default.'
                }
            ]
        },
        'config.options': {
            title: '⚡ Options',
            sections: [
                {
                    heading: 'Enable plugin',
                    text: 'Enables or disables the joystick override. When disabled, yaw returns to direct joystick control with no processing.'
                },
                {
                    heading: 'Smoothing',
                    text: 'Enables or disables the input signal smoothing filter.'
                },
                {
                    heading: 'Dead zone',
                    text: 'Enables or disables the center dead zone.'
                },
                {
                    heading: 'Auto-coordination',
                    text: 'Enables or disables the automatic yaw correction during bank.'
                },
                {
                    heading: 'Yaw damper',
                    text: 'Enables or disables the yaw damper.'
                }
            ]
        }
    }
};

let currentInfoKey = null;

function openInfo(key) {
    const lang = (typeof currentLang !== 'undefined') ? currentLang : 'fr';
    const data = INFO_DATA[lang]?.[key] || INFO_DATA.fr[key];
    if (!data) return;
    currentInfoKey = key;

    const modal = document.getElementById('info-modal');
    const title = document.getElementById('info-title');
    const body = document.getElementById('info-body');

    title.textContent = data.title;
    body.innerHTML = data.sections.map(s =>
        `<div class="info-section">
            <div class="info-heading">${s.heading}</div>
            <div class="info-text">${s.text.replace(/\n/g, '<br>')}</div>
        </div>`
    ).join('');

    modal.classList.add('open');
}

function closeInfo() {
    document.getElementById('info-modal').classList.remove('open');
    currentInfoKey = null;
}

// Close on backdrop click, close button, or Escape
function _initInfoModal() {
    const modal = document.getElementById('info-modal');
    const closeBtn = modal?.querySelector('.info-close');

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeInfo();
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeInfo();
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeInfo();
    });
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _initInfoModal);
} else {
    _initInfoModal();
}

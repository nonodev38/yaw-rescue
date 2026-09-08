/**
 * AUTO-YAW DECK — Readme content (FR / EN)
 * Displayed in a modal from the connection page.
 */

const README_DATA = {
    fr: {
        title: '📖 Manuel utilisateur',
        sections: [
            {
                heading: 'Architecture',
                text: 'Le script Lua bridge lit les datarefs X-Plane et écrit data/state.txt.\nLe serveur Python lit ce fichier et le sert via une API REST en HTTPS.\nLe smartphone affiche les données et permet d\'envoyer des commandes.\nLes commandes sont écrites dans data/commands.txt et lues par le Lua.'
            },
            {
                heading: 'Prérequis',
                text: '• Python 3.7+ (avec tkinter pour le panneau GUI)\n• X-Plane 11/12 avec FlyWithLua NXT\n• Le script auto_yaw.lua actif dans Scripts/\n• PC et smartphone sur le même réseau WiFi\n\nLes packages Python sont installés automatiquement au premier lancement.'
            },
            {
                heading: 'Installation',
                text: '1. Copiez le dossier "Auto Yaw Deck" dans Scripts/ :\n   X-Plane/Resources/plugins/FlyWithLua/Scripts/Auto Yaw Deck/\n\n2. Placez auto_yaw_deck.lua à la racine de Scripts/ (pas dans le sous-dossier) :\n   X-Plane/Resources/plugins/FlyWithLua/Scripts/auto_yaw_deck.lua\n\n3. Double-cliquez sur start_panel.bat pour lancer le panneau de contrôle\n\n4. Scannez le QR code avec votre téléphone et acceptez le certificat SSL'
            },
            {
                heading: 'Interface mobile',
                text: '⚙️ Config : Lissage, filtre anti-bruit, zone morte, auto-coordination, yaw damper\n\n🎛️ Contrôles : Boussole avec cap retour, sliders trim (profondeur/aileron/direction), volets\n\n📡 Télémétrie : Cap, altitude, vitesse, banque, état Yaw Rescue, profil actif'
            },
            {
                heading: 'Système de trim',
                text: 'Les trims sont appliqués comme offsets directs sur les sorties joystick.\nÇa fonctionne sur TOUS les avions, même ceux sans compensateurs physiques.\n\nProfondeur (Pitch) : offset sur l\'axe Y\nAilerons (Roll) : offset sur l\'axe X\nDirection (Yaw) : offset sur l\'axe de lacet'
            },
            {
                heading: 'Cap retour',
                text: 'Le bouton "Cap retour" fige la position actuelle et affiche une flèche\njaune à la position opposée (180°). Utile pour revenir à l\'aéroport de départ.\n\n• 1er clic : enregistre le cap et affiche la flèche\n• 2ème clic : masque la flèche (le cap est préservé)\n• Bouton "Effacer" : réinitialise pour enregistrer un nouveau cap\n\nLe cap retour est automatiquement réinitialisé lors du chargement d\'un nouvel avion.'
            },
            {
                heading: 'Filtre anti-bruit',
                text: 'Détecte les oscillations rapides du joystick (bruit de potentiomètre).\nSi la variation dépasse le seuil, l\'entrée est rejetée.\n\nSeuil : 0.00 (désactivé) à 0.30 (agressif). Défaut : 0.05'
            },
            {
                heading: 'Synchronisation',
                text: 'Les modifications sont synchronisées entre le panneau FlyWithLua\net l\'interface web dans les deux sens.\n\nLes paramètres sont sauvegardés dans AutoYaw_profiles.cfg.'
            },
            {
                heading: 'Certificat SSL',
                text: 'Le serveur génère automatiquement un certificat auto-signé.\nSi votre téléphone bloque le certificat :\n\n1. Ouvrez http://IP_PC:8080/cert sur votre téléphone\n2. Téléchargez autoyawdeck-ca.pem\n3. Android : Paramètres > Sécurité > Installer un certificat > AC\n4. Rouvrez l\'URL HTTPS — le certificat est maintenant reconnu'
            },
            {
                heading: 'Sécurité et confidentialité',
                text: '• 100% local — aucune donnée envoyée sur Internet\n• Votre PC et votre téléphone communiquent uniquement via votre réseau WiFi privé\n• Certificat SSL auto-signé pour la communication chiffrée\n• Le serveur écoute uniquement sur le réseau local (LAN)\n• Les commandes sont validées par le Lua bridge avant application'
            },
            {
                heading: 'Dépannage',
                text: '• Vérifiez que auto_yaw_deck.lua est à la racine de Scripts/\n• Vérifiez que data/state.txt est mis à jour\n• PC et smartphone sur le même réseau WiFi\n• Essayez le mode --no-cert pour les tests\n• Le port 8443 ne doit pas être utilisé par un autre programme'
            }
        ]
    },
    en: {
        title: '📖 User Manual',
        sections: [
            {
                heading: 'Architecture',
                text: 'The Lua bridge script reads X-Plane datarefs and writes data/state.txt.\nThe Python server reads this file and serves it via REST API over HTTPS.\nThe smartphone displays data and sends commands (trims, config, flaps).\nCommands are written to data/commands.txt and read by the Lua bridge.'
            },
            {
                heading: 'Requirements',
                text: '• Python 3.7+ (with tkinter for the GUI panel)\n• X-Plane 11/12 with FlyWithLua NXT plugin\n• auto_yaw.lua script active in Scripts/\n• PC and smartphone on the same WiFi network\n\nPython packages are installed automatically on first run.'
            },
            {
                heading: 'Installation',
                text: '1. Copy the "Auto Yaw Deck" folder into Scripts/ :\n   X-Plane/Resources/plugins/FlyWithLua/Scripts/Auto Yaw Deck/\n\n2. Place auto_yaw_deck.lua in Scripts/ root (not inside the subfolder) :\n   X-Plane/Resources/plugins/FlyWithLua/Scripts/auto_yaw_deck.lua\n\n3. Double-click start_panel.bat to launch the control panel\n\n4. Scan the QR code with your phone and accept the SSL certificate'
            },
            {
                heading: 'Mobile Interface',
                text: '⚙️ Config: Smoothing, noise filter, dead zone, auto-coordination, yaw damper\n\n🎛️ Controls: Compass with return heading, trim sliders (pitch/roll/yaw), flaps\n\n📡 Telemetry: Heading, altitude, airspeed, bank, Yaw Rescue state, active profile'
            },
            {
                heading: 'Trim System',
                text: 'Trims are applied as direct offsets to the joystick override outputs.\nThis works on ALL aircraft, even those without physical trim tabs.\n\nPitch (Elevator): offset on the Y axis\nRoll (Ailerons): offset on the X axis\nYaw (Rudder): offset on the yaw axis'
            },
            {
                heading: 'Return Heading',
                text: 'The "Return heading" button freezes the current heading and shows a\nyellow arrow at the opposite position (180°). Useful for returning to the departure airport.\n\n• 1st click: records heading and shows arrow\n• 2nd click: hides arrow (heading is preserved)\n• "Clear" button: resets to record a new heading\n\nThe return heading is automatically reset when a new aircraft is loaded.'
            },
            {
                heading: 'Noise Filter',
                text: 'Detects rapid joystick oscillations (potentiometer jitter).\nIf the variation exceeds the threshold, the input is rejected.\n\nThreshold: 0.00 (off) to 0.30 (aggressive). Default: 0.05'
            },
            {
                heading: 'Synchronization',
                text: 'Changes are synchronized between the FlyWithLua panel\nand the web interface in both directions.\n\nSettings are saved to AutoYaw_profiles.cfg for persistence.'
            },
            {
                heading: 'SSL Certificate',
                text: 'The server auto-generates a self-signed SSL certificate.\nIf your phone blocks the certificate:\n\n1. Open http://PC_IP:8080/cert on your phone\n2. Download autoyawdeck-ca.pem\n3. Android: Settings > Security > Install certificate > CA\n4. Reopen the HTTPS URL — the certificate is now trusted'
            },
            {
                heading: 'Security & Privacy',
                text: '• 100% local — no data sent to the Internet\n• Your PC and phone communicate only through your private WiFi network\n• Self-signed SSL certificate for encrypted communication\n• Server listens only on the local network (LAN)\n• Commands are validated by the Lua bridge before application'
            },
            {
                heading: 'Troubleshooting',
                text: '• Verify auto_yaw_deck.lua is in Scripts/ root (not in Auto Yaw Deck/)\n• Check that data/state.txt is being updated\n• PC and smartphone on the same WiFi network\n• Try --no-cert mode for testing\n• Port 8443 must not be used by another program'
            }
        ]
    }
};

let readmeModalOpen = false;

function openReadme() {
    const lang = (typeof currentLang !== 'undefined') ? currentLang : 'fr';
    const data = README_DATA[lang] || README_DATA.fr;

    const modal = document.getElementById('readme-modal');
    const title = document.getElementById('readme-title');
    const body = document.getElementById('readme-body');

    title.textContent = data.title;
    body.innerHTML = data.sections.map(s =>
        `<div class="info-section">
            <div class="info-heading">${s.heading}</div>
            <div class="info-text">${s.text.replace(/\n/g, '<br>')}</div>
        </div>`
    ).join('');

    modal.classList.add('open');
    readmeModalOpen = true;
}

function closeReadme() {
    document.getElementById('readme-modal').classList.remove('open');
    readmeModalOpen = false;
}

// Setup event listeners
(function() {
    function init() {
        const modal = document.getElementById('readme-modal');
        const closeBtn = modal?.querySelector('.info-close');

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeReadme();
            });
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeReadme();
            });
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

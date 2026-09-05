# Auto-Yaw Deck

Pilotage X-Plane depuis votre smartphone — panneau de contrôle remote pour le script Auto-Yaw.

## Principe

```
┌─────────────┐    fichiers JSON    ┌──────────────┐    HTTPS/WiFi    ┌─────────────┐
│  X-Plane     │ ←────────────────→ │ Python Server │ ←─────────────→ │ Smartphone  │
│  (Lua FWL)  │   state.txt        │  (port 8443)  │   QR code →    │ (navigateur)│
│              │   commands.txt     │               │                │             │
└─────────────┘                    └──────────────┘                └─────────────┘
```

1. Le script Lua `auto_yaw_deck.lua` écrit l'état des datarefs X-Plane dans `data/state.txt`
2. Le serveur Python lit ce fichier et le sert via une API REST en HTTPS
3. Le smartphone affiche les données et permet d'envoyer des commandes (trims, volets, config)
4. Les commandes sont écrites dans `data/commands.txt` et lues par le script Lua

## Prérequis

- Python 3.7+ avec `openssl` dans le PATH (pour le certificat SSL)
- X-Plane avec FlyWithLua NXT
- Le script `auto_yaw.lua` actif dans `Scripts/`

## Utilisation

### 1. Démarrer le serveur

```bash
cd "Scripts/Auto Yaw Deck"
python server.py
```

Options :
- `--port 8443` : Port du serveur HTTPS (défaut: 8443)
- `--cert-port 8080` : Port HTTP utilisé uniquement pour télécharger le certificat (défaut: 8080)
- `--no-cert` : Mode HTTP sans SSL (pour tests uniquement, certains téléphones forcent
  quand même une négociation TLS et ce mode ne fonctionnera pas dans ce cas)

### 2. Charger le script Lua

FlyWithLua ne charge pas les scripts placés dans un sous-dossier de `Scripts/` :
`auto_yaw_deck.lua` doit donc se trouver directement dans `Scripts/`, à côté de
`auto_yaw.lua` (et non dans `Scripts/Auto Yaw Deck/`). Il est déjà placé à cet
 endroit ; ne le déplacez pas dans ce sous-dossier sous peine qu'il ne soit plus
détecté par FlyWithLua. Il retrouve seul ses fichiers de données dans
`Scripts/Auto Yaw Deck/data/`.

### 3. Connecter le smartphone

1. Le serveur affiche un QR code dans le terminal
2. Scannez-le avec votre téléphone
3. **Acceptez l'avertissement SSL** (certificat auto-signé)
4. Le panneau de contrôle s'affiche

### 4. Utiliser l'interface

- **📡 Télémétrie** : Affiche en temps réel les données de vol (cap, altitude, vitesse, banque) et l'état d'Auto-Yaw
- **🎛️ Contrôles** : Sliders pour trim profondeur/aileron/direction et volets
- **⚙️ Config** : Réglages du lissage, zone morte, auto-coordination, yaw damper

## Fichiers

```
Scripts/
├── auto_yaw_deck.lua       # Script pont Lua ↔ serveur (à la racine de Scripts/,
│                          # FlyWithLua ne scanne pas les sous-dossiers)
└── Auto Yaw Deck/
    ├── server.py           # Serveur HTTPS Python
    ├── static/
    │   ├── index.html      # Interface web
    │   ├── style.css       # Styles
    │   └── app.js          # JavaScript client
    ├── data/               # (créé automatiquement)
    │   ├── state.txt       # Écrit par Lua, lu par Python
│   └── commands.txt       # Écrit par Python, lu par Lua
├── certs/                 # (créé automatiquement)
│   ├── server.pem         # Certificat SSL auto-signé
│   └── server.key         # Clé privée SSL
└── README.md
```

## Dépannage

**Le serveur ne démarre pas**
- Vérifiez que Python 3.7+ est installé : `python --version`
- Vérifiez que le port 8443 n'est pas utilisé

**Le smartphone ne peut pas se connecter**
- Assurez-vous que le PC et le smartphone sont sur le même réseau WiFi (pas le partage
  de connexion de l'un des deux téléphones eux-mêmes)
- Acceptez l'avertissement SSL dans le navigateur du téléphone

**Le téléphone bloque le certificat sans option "continuer quand même"**
(fréquent sur Samsung Internet/Knox "Wi-Fi sécurisé")
1. Sur le téléphone, ouvrez l'URL affichée dans le terminal, ex.
   `http://IP_DU_PC:8080/cert` (HTTP simple, pas d'avertissement possible ici)
2. Téléchargez le fichier `autoyawdeck-ca.pem`
3. Android : Paramètres > Sécurité > Chiffrement et identifiants > Installer un
   certificat > Certificat d'AC, puis sélectionnez le fichier téléchargé
4. Rouvrez l'URL HTTPS principale : le certificat est maintenant reconnu comme
   fiable et l'avertissement disparaît

**Les données ne s'affichent pas**
- Vérifiez que `auto_yaw_deck.lua` est bien à la racine de `Scripts/` (pas dans
  `Scripts/Auto Yaw Deck/`) et qu'il est chargé dans FlyWithLua
- Vérifiez que `data/state.txt` existe et est mis à jour
- Regardez les logs de la console X-Plane

## Sécurité

- Le serveur utilise un certificat SSL auto-signé
- Il écoute uniquement sur le réseau local (LAN)
- Aucune donnée n'est envoyée vers Internet
- Les commandes sont validées côté Lua avant application

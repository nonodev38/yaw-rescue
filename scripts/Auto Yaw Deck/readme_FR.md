<div align="center">

# ✈️ AUTO-YAW DECK

### 🎮 *Contrôle de X-Plane à distance via smartphone*

<img src="logo.png" alt="Auto-Yaw Deck" width="160"/>

**Corrigez votre yaw. Pilotez votre avion. 🛩️ Tout depuis votre téléphone.**

<span style="color:#22b8a6">✅ Compatible X-Plane 11 & 12</span> • <span style="color:#3b82f6">📱 Interface web mobile</span> • <span style="color:#f59e0b">🇫🇷 🇬🇧 FR / EN</span> • <span style="color:#ef4444">🔒 100% local, chiffré SSL</span>

---

</div>

> 🎯 **Qu'est-ce que c'est ?**
>
> Surveillez la **télémétrie en direct**, réglez les **trims**, configurez les **filtres Auto-Yaw**, gérez vos **volets et trains** — le tout depuis une interface web mobile soignée au thème sombre, sur votre propre WiFi. Pas d'internet, pas de cloud, aucune donnée ne quitte votre réseau.

---

## 🧭 Sommaire

| | |
|---|---|
| 1️⃣ [Architecture](#-architecture) | 9️⃣ [Système de trim](#-système-de-trim--comment-ça-marche) |
| 2️⃣ [Prérequis](#-prérequis) | 🔟 [Détection de X-Plane](#-détection-de-x-plane) |
| 3️⃣ [Installation](#-installation) | 1️⃣1️⃣ [Filtre anti-bruit expliqué](#-filtre-anti-bruit--comment-ça-marche) |
| 4️⃣ [Structure des fichiers](#-structure-des-fichiers) | 1️⃣2️⃣ [Certificat SSL](#-certificat-ssl) |
| 5️⃣ [Panneau de contrôle graphique](#-utilisation--panneau-de-contrôle-graphique) | 1️⃣3️⃣ [Dépannage](#-dépannage) |
| 6️⃣ [Serveur en ligne de commande](#-utilisation--serveur-en-ligne-de-commande) | 1️⃣4️⃣ [Sécurité](#-sécurité) |
| 7️⃣ [Fonctionnalités de l'interface web](#-fonctionnalités-de-linterface-web) | 1️⃣5️⃣ [Options en ligne de commande](#-options-en-ligne-de-commande) |
| 8️⃣ [Synchronisation bidirectionnelle](#-synchronisation-bidirectionnelle) | |

---

## 🧱 Architecture

```
+-------------+   state.txt    +--------------+   HTTPS/WiFi   +-----------+
|  ✈️ X-Plane  | <=============> | 🐍 Serveur   | <============> | 📱 Phone  |
|  (Lua FWL)  |   commands.txt  | Python       |   QR code ->   | (browser) |
+-------------+                | (port 8443)  |                +-----------+
                               +--------------+
```

**Comment circulent les données :**

1. 🟦 Le **pont Lua** lit les datarefs de X-Plane → écrit dans `data/state.txt`
2. 🟩 Le **serveur Python** lit `state.txt` → le sert via une API REST (HTTPS)
3. 🟨 Votre **smartphone** affiche les données en direct & envoie des commandes (trims, config, volets)
4. 🟥 Les commandes sont écrites dans `data/commands.txt` → lues par le pont Lua

---

## ✅ Prérequis

| Exigence | Note |
|---|---|
| <span style="color:#22b8a6">🐍 **Python 3.7+**</span> | avec `tkinter` pour le panneau graphique |
| <span style="color:#3b82f6">✈️ **X-Plane 11 / 12**</span> | avec le plugin FlyWithLua NXT |
| <span style="color:#3b82f6">📜 **`auto_yaw.lua` actif**</span> | dans le dossier `Scripts/` de FlyWithLua |
| <span style="color:#f59e0b">📶 **Même réseau WiFi**</span> | PC + smartphone |

> 📦 Les packages Python sont **installés automatiquement au premier lancement** :
> `cryptography` (certificat SSL) + `qrcode[pil]` (QR code)

---

## 📥 Installation

**1️⃣** Copiez le dossier `Auto Yaw Deck` dans votre répertoire Scripts de FlyWithLua :

```
X-Plane 12/Resources/plugins/FlyWithLua/Scripts/Auto Yaw Deck/
```

**2️⃣** Placez `auto_yaw_deck.lua` dans le dossier `Scripts/` — **PAS** dans `Auto Yaw Deck/` :

```
X-Plane 12/Resources/plugins/FlyWithLua/Scripts/auto_yaw_deck.lua
```

> ⚠️ **Important :** FlyWithLua ne charge que les scripts situés à la **racine** du dossier `Scripts/` !

**3️⃣** Lancez le panneau de contrôle → double-cliquez sur **`start_panel.bat`** 🖱️

**4️⃣** Scannez le 📱 **QR code** affiché dans le panneau

**5️⃣** Acceptez l'avertissement 🔐 **de certificat SSL** dans le navigateur de votre téléphone

---

## 🗂️ Structure des Fichiers

```
Scripts/
├── auto_yaw_deck.lua          🟦 Pont Lua (doit être à la racine de Scripts/)
└── Auto Yaw Deck/
    ├── panel.py               🖥️  Panneau de contrôle graphique (tkinter)
    ├── server.py              🐍 Serveur HTTPS (Python)
    ├── start_panel.bat        🪟 Lanceur Windows
    ├── info.js                ℹ️  Panneaux d'info de la section Config
    ├── static/
    │   ├── index.html         🌐 Interface web
    │   ├── style.css          🎨 Thème aviation sombre
    │   ├── config.js          ⚙️  Constantes réglables (scrutation, debounce)
    │   ├── i18n.js            🌍 Traductions (FR/EN) + gestion de la langue
    │   ├── state.js           📊 Scrutation de l'état + garde anti-écrasement
    │   ├── api.js             📡 Envoi des commandes au serveur
    │   ├── sliders.js         🎚️  Widgets curseurs (pas, centre, diagrammes)
    │   ├── ui.js              🧩 Références DOM, onglets, navigation, statut
    │   ├── compass.js         🧭 Compas + cap de retour
    │   ├── actions.js         🔘 Réinit. trims / actions volets
    │   └── main.js            🚀 Amorçage (init + nettoyage)
    ├── data/                  ⚙️  (créé automatiquement)
    │   ├── state.txt          📝 Écrit par Lua, lu par Python
    │   ├── commands.txt       📝 Écrit par Python, lu par Lua
    │   ├── prefs.json         💾 Préférences sauvegardées (langue de l'UI…)
    │   └── flight.json        🛫 Généré lors de la reprise au dernier aéroport
    └── certs/                 🔐 (créé automatiquement)
        ├── server.pem         🔑 Certificat SSL auto-signé
        └── server.key         🔑 Clé privée SSL
```

---

## 🖥️ Utilisation — Panneau de Contrôle Graphique

Double-cliquez sur **`start_panel.bat`** et le panneau vous montre tout :

| Affichage | Description |
|---|---|
| 📡 **État du serveur** | URL, port, mode HTTPS/HTTP |
| 🎮 **Détection de X-Plane** | en cours d'exécution ✅ / non détecté ⚠️ / introuvable ❌ |
| 🛫 **Dernier aéroport** | depuis `Freeflight.prf` (+ secours `log.txt`), avec la case *« Reprendre au dernier aéroport »* (✅ par défaut) |
| 📱 **QR code** | connexion instantanée du téléphone |
| ▶️ **Démarrer X-Plane** | seulement si détecté mais non lancé — reprend au dernier aéroport si la case est cochée |
| ⏹️ **Fermer le serveur** | arrête tout |

### 🛫 Reprendre au dernier aéroport

Quand X-Plane ne tourne pas, le panneau lit l'aéroport (et la piste 🛬) de la dernière session :

1. `Output/preferences/Freeflight.prf` (`_last_start` / `_airport`)
2. `log.txt` — dernière ligne `I/FLT: Init … apt:XXXX`

Un clic sur **« Démarrer X-Plane »** lance le simulateur avec :

```bash
--new_flight_json=<data/flight.json>
```

…pour démarrer **directement à cet aéroport** ✈️ (nécessite **X-Plane 12.4+**). Décochez la case pour démarrer à l'emplacement par défaut.

### 🖥️ Panneau — ligne de commande

```bash
python panel.py              # 🔒 Mode HTTPS (par défaut)
python panel.py --no-cert    # 🚫 Mode HTTP (test uniquement)
python panel.py --port 9000  # 🔢 Port personnalisé
```

> 🤫 La fenêtre console se **réduit automatiquement** à l'ouverture du panneau — c'est normal !

---

## 💻 Utilisation — Serveur en Ligne de Commande

Pas de panneau graphique ? Démarrez le serveur directement :

```bash
python server.py              # 🔒 Mode HTTPS (par défaut)
python server.py --no-cert    # 🚫 Mode HTTP (test uniquement)
python server.py --port 9000  # 🔢 Port personnalisé
```

> 📱 Le serveur affiche un **QR code directement dans le terminal** — scannez-le avec votre téléphone.

---

## 🌐 Fonctionnalités de l'Interface Web

L'interface web mobile comporte **3 onglets** 🗂️ :

### ⚙️ ONGLET CONFIG *(par défaut)*

| Réglage | Ce qu'il fait | Plage | Défaut |
|---|---|---|---|
| 🎚️ **Lissage du signal** | Filtre à moyenne mobile exponentielle | 0,01 (fort) → 0,50 (faible) | `0,15` |
| 🧹 **Filtre anti-bruit** | Rejette la gigue rapide du joystick | 0,00 (désactivé) → 0,30 (agressif) | `0,05` |
| 🎯 **Zone morte** | Ignore les petits mouvements au centre | 0,00 (désactivée) → 0,20 | `0,03` |
| 🔄 **Auto-Coordination** | Correction de lacet ∝ inclinaison — gain / limite d'inclinaison | 0,00–1,00 / 5–60° | `0,40` / `35` |
| 🌀 **Yaw Damper** | Réduit le roulis hollandais par rétroaction — gain / sensibilité | 0,00–1,00 / 0,5–5,0 | `0,30` / `2,0` |

**Options (interrupteurs) :** activer/désactiver le plugin, le lissage, la zone morte, l'auto-coordination et le yaw damper.

> ℹ️ Chaque section possède un bouton d'information **(i)** qui ouvre un panneau d'explication détaillé.

### 🎛️ ONGLET CONTRÔLES

- 🧭 **Compas** — rose rotative temps réel + ligne de foi fixe, affiche le cap magnétique
- 🔙 **Cap de retour** — fige le cap actuel, une flèche jaune pointe le cap **opposé** (180°). *1er clic* enregistre et affiche, *2e clic* masque, **Effacer** réinitialise.
- 🎚️ **Curseurs de Trim** — Tangage 🡕 / Roulis 🡘 / Lacet 🡔 entre **−1,0 et +1,0**, appliqués en décalages directs → fonctionne sur **TOUS** les avions (même sans plans de trimmage !)
- 🦅 **Volets** — curseur 0–100 % + boutons prédéfinis `0 % / 1/3 / 2/3 / Full`

### 📡 ONGLET TÉLÉMÉTRIE

| Donnée | Lecture |
|---|---|
| 🧭 **Données de vol** | Cap (°), Altitude (ft), Vitesse (kts), Inclinaison (°) |
| ⚙️ **État Auto-Yaw** | Entrée brute / lissée / sortie finale, sorties auto-coord. & damper, profil actif |
| ✈️ **Avion** | Nom détecté par X-Plane |

---

## 🔄 Synchronisation Bidirectionnelle

Tout ce que vous changez sur votre **téléphone** se reflète dans le **panneau FlyWithLua** — et inversement. Les deux lisent la même table de configuration globale.

```
X-Plane → Web :   auto_yaw.lua → state.txt → API Python → affichage Web
Web → X-Plane :   commande Web → commands.txt → auto_yaw_deck.lua → auto_yaw.lua
```

> 💾 Tous les réglages sont aussi sauvegardés dans `AutoYaw_profiles.cfg` pour la persistance.

---

## 🌍 Support des Langues

> 🇫🇷 **Français** &nbsp;|&nbsp; 🇬🇧 **English** — changez avec le bouton **EN/FR** dans l'en-tête.

La préférence est sauvegardée **à la fois** dans le navigateur (`localStorage`) **et** côté serveur dans `data/prefs.json`, elle survit donc :
- 🔄 aux redémarrages de X-Plane
- 🌐 aux changements d'adresse IP
- 📱 sur **tous les appareils** connectés au panneau

Tout est traduit : libellés d'onglets, en-têtes de cartes, curseurs, page de connexion, badges d'état, panneaux d'info.

---

## 🎚️ Système de Trim — Comment Ça Marche

> ❌ Les datarefs de trim traditionnels de X-Plane ne fonctionnent que sur les avions dotés de **plans de trimmage physiques** (ex. le stabilisateur horizontal du Cessna 172). Les avions sans trimmage d'ailerons ou de gouverne **ignorent** ces datarefs.

✅ **Auto-Yaw Deck** applique les valeurs de trim en **DÉCALAGES DIRECTS** sur les sorties d'override du joystick (`sim/joystick/yoke_*_ratio`) :

```
pitch_output = raw_pitch + elevator_trim   🡕  Tangage
roll_output  = raw_roll  + aileron_trim    🡘  Roulis
yaw_output   = yaw_auto  + rudder_trim     🡔  Lacet
```

> 🎉 Cette approche fonctionne **universellement sur TOUS les avions** de X-Plane !

---

## 📡 Détection de X-Plane

Le serveur vérifie l'**horodatage** dans `state.txt` (le pont Lua écrit `os.time()` à chaque frame). S'il date de moins de **5 secondes**, X-Plane est considéré comme **actif**.

| Statut | Couleur | Signification |
|---|---|---|
| 🟥 **HORS LIGNE** | rouge | Pas de connexion au serveur |
| 🟧 **EN ATTENTE** | orange | Serveur actif, X-Plane non détecté |
| 🟩 **EN DIRECT** | vert | Serveur + X-Plane tous deux actifs |

> ✈️ Quand un nouvel avion est chargé, le cap de retour se réinitialise et se ré-enregistre automatiquement.

---

## 🧹 Filtre Anti-Bruit — Comment Ça Marche

Les potentiomètres de joystick produisent de rapides **oscillations** (« gigue »), surtout près du centre. Le filtre compare les valeurs brutes consécutives :

```
Si |valeur_brute − valeur_précédente| > seuil :
    🚫 Rejeter l'entrée → conserver la valeur lissée précédente
Sinon :
    ✅ Appliquer le lissage normal
```

**Conseils de réglage :**

| Valeur | Effet |
|---|---|
| `0,00` | 🚫 Désactivé (aucun filtrage) |
| `0,05` | 👍 Défaut — bon pour la plupart des joysticks |
| `0,10–0,15` | 💪 Agressif — pour les potentiomètres très bruyants |

---

## 🔐 Certificat SSL

Le serveur génère automatiquement un **certificat SSL auto-signé** (bibliothèque Python `cryptography`) :
- 🔑 Paire de clés RSA-2048
- 📜 X.509 v3 avec Subject Alternative Names (**toutes les IP locales**)
- ⏳ Valide **365 jours**

**Le téléphone bloque le certificat ?**

1. 📲 Ouvrez `http://IP_DE_VOTRE_PC:8080/cert` dans le navigateur du téléphone
2. ⬇️ Téléchargez `autoyawdeck-ca.pem`
3. 🛡️ *Android :* Paramètres > Sécurité > Installer un certificat > **Certificat d'autorité de certification**
4. 🔁 Rouvrez l'URL HTTPS — maintenant reconnue !

> 🌐 Le serveur de téléchargement du certificat tourne sur un **port HTTP séparé** (défaut `8080`) pour permettre l'installation du certificat sans avertissements TLS.

---

## 🛠️ Dépannage

<details>
<summary><b>🛑 Le serveur ne démarre pas ?</b></summary>

- ✅ `start_panel.bat` **détecte automatiquement Python** (`py -3` / `python` / `python3`), vérifie tkinter et affiche des instructions claires
- 🐍 Vérifiez la version de Python : `python --version` (**3.7+** requis)
- 🔌 Le **port 8443** est-il déjà utilisé ? (le lanceur vous en avertit)
- 🧪 Essayez le mode `--no-cert` pour les tests

</details>

<details>
<summary><b>📱 Le téléphone ne se connecte pas ?</b></summary>

- 📶 Le PC et le téléphone doivent être sur le **même réseau WiFi**
- 🚫 Pas de données mobiles ni de partage de connexion du téléphone
- 🔐 Acceptez l'avertissement de certificat SSL dans le navigateur

</details>

<details>
<summary><b>🛡️ Samsung / Knox bloque le certificat ?</b></summary>

- 📖 Suivez la section [Certificat SSL](#-certificat-ssl) ci-dessus
- 📲 Installez le certificat d'autorité depuis la page de téléchargement HTTP

</details>

<details>
<summary><b>👻 Aucune donnée ne s'affiche sur le téléphone ?</b></summary>

- 📂 Vérifiez que `auto_yaw_deck.lua` est à la racine de `Scripts/` (pas dans `Auto Yaw Deck/`)
- 📝 Vérifiez que `data/state.txt` est mis à jour (consultez les logs de X-Plane)
- 🖥️ Vérifiez la console du serveur Python pour d'éventuelles erreurs

</details>

<details>
<summary><b>🎚️ Les curseurs de trim n'affectent pas l'avion ?</b></summary>

- 📜 Assurez-vous que `auto_yaw.lua` est chargé et le plugin **activé**
- ✅ Vérifiez que l'override est actif (**ACTIVE** dans le panneau FlyWithLua)
- 🔧 Les trims agissent en décalages sur l'override du joystick → le plugin **doit être activé**

</details>

---

## 🔒 Sécurité

| | |
|---|---|
| 🔐 | Certificat SSL auto-signé pour une communication locale chiffrée |
| 🌐 | Le serveur n'écoute **que** sur le réseau local (LAN) |
| 🚫 | Aucune donnée n'est jamais envoyée sur Internet |
| 🛡️ | Commandes validées par le pont Lua avant application |
| ⏳ | Certificat auto-expirant après 365 jours (régénéré au prochain démarrage) |

---

## ⚙️ Options en Ligne de Commande

**`server.py` :**

| Option | Description | Défaut |
|---|---|---|
| `--port PORT` | Port HTTPS | `8443` |
| `--cert-port PORT` | Port HTTP pour le téléchargement du certificat | `8080` |
| `--cert-dir DIR` | Répertoire des certificats | `certs/` |
| `--no-cert` | Mode HTTP uniquement (sans SSL) | — |

**`panel.py` :**

| Option | Description | Défaut |
|---|---|---|
| `--port PORT` | Port HTTPS | `8443` |
| `--cert-port PORT` | Port HTTP pour le téléchargement du certificat | `8080` |
| `--no-cert` | Mode HTTP uniquement (sans SSL) | — |

---

<div align="center">

### ✈️ Bon vol — et profitez d'un yaw parfaitement lisse ! 🛩️

<img src="logo.png" alt="Auto-Yaw Deck" width="80"/>

</div>

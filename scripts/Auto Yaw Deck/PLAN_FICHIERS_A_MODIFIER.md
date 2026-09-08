# 📂 Plan de refactor — Yaw Rescue / Auto Yaw Deck

Document de pilotage du chantier : **état actuel**, **arborescence cible**,
**migration des chemins (JS & PY) à faire au fil du code**, bugs corrigés,
et feuille de route étape par étape.

> ⚠️ **Règle de sécurité** : chaque étape doit conserver le comportement.
> Après chaque étape : `python -m py_compile *.py` + `node --check static/**/*.js`
> + serveur relancé (baseline P0) avant de passer à la suivante.

---

## 1. État actuel du projet

Tailles **réelles** (relevé du 08/09/2026, après les phases P1→P5.1) :

| Fichier | Lignes | Rôle |
|---|---|---|
| `panel.py` | 644 | GUI Tkinter + orchestration (entry point) |
| `static/index.html` | 484 | page web (connexion + 3 onglets) |
| `static/css/widgets.css` | 457 | contrôles, boussole, boutons, toggles |
| `static/ui.js` | 336 | UI : onglets, navigation, `updateUI()` |
| `server.py` | 263 | serveur HTTP (entry point, orchestré) |
| `static/i18n.js` | 258 | traductions FR/EN de l'app web |
| `static/info.js` | 257 | contenus d'aide ⓘ (Config) |
| `deck_http.py` | 255 | `DeckHTTPHandler` + routes/API |
| `deck_state.py` | 240 | état X-Plane, cache, commandes |
| `deck_cert.py` | 211 | réseau + certificat auto-signé |
| `static/css/modal.css` | 196 | modales, langue, flash |
| `deck_xplane.py` | 195 | détection X-Plane |
| `static/sliders.js` | 152 | sliders ±, toggles, diagramme trim |
| `deck_installer.py` | 136 | installation FlyWithLua / Auto Yaw Deck |
| `static/compass.js` | 135 | boussole + rose (générée, P4.1) |
| `deck_flight.py` | 134 | reprise de vol, `start_xplane` |
| `static/readme.js` | 130 | modale À propos / dépannage |
| `static/config.js` | 125 | cartes Config (générées, P4.2) |
| `static/vitals.js` | 117 | jauges train/RPM/FPM/AOA |
| `static/css/responsive.css` | 110 | media queries |
| `deck_instance.py` | 100 | PID + kill instances |
| `deck_panel_i18n.py` | 93 | `PANEL_I18N` FR/EN |
| `static/state.js` | 60 | polling `/api/state` |
| `deck_runner.py` | 57 | thread serveur du panel |
| `static/main.js` | 55 | boot / point d'entrée JS |
| `static/modal.js` | 44 | modales communes (P5.1) |
| `static/css/theme.css` | 40 | variables `:root`, reset |
| `deck_prefs.py` | 34 | `load_prefs` / `save_prefs` |
| `static/actions.js` | 29 | `resetTrims`, `setFlaps` |
| `static/api.js` | 22 | POST commandes |
| `deck_log.py` | 21 | `dlog()`, `DEBUG_LOGGING` |
| `deck_paths.py` | 15 | chemins partagés |

Autres fichiers : `aerodev-yawrescue.html` (page vitrine, **conservée** par
décision), `changelog.txt` (géré à la main, **conservé**), `readme_FR.md` /
`readme_EN.md` (docs), `start_panel.bat` (lanceur Windows), `launcher.txt`,
`translations.lua`, `logo.png`, dossiers `data/` et `certs/`.

---

## 2. 🎯 Arborescence cible (plus professionnelle)

Objectif : regrouper la logique par couche, **isoler les entry points**,
et séparer clairement code / ressources / runtime / docs.

```
Auto Yaw Deck/
├── panel.py                  # ENTRY POINT — GUI Tkinter (reste à la racine)
├── server.py                 # ENTRY POINT — serveur HTTP (reste à la racine)
├── start_panel.bat           # lanceur Windows (reste à la racine)
│
├── deck/                     # 📦 PACKAGE Python (remplace les deck_*.py plats)
│   ├── __init__.py           #    ré-exports publics (compat panel/server)
│   ├── paths.py              #    chemins partagés (ex deck_paths.py)
│   ├── log.py                #    dlog(), DEBUG_LOGGING (ex deck_log.py)
│   ├── prefs.py              #    load/save prefs (ex deck_prefs.py)
│   ├── state.py              #    état X-Plane, commandes (ex deck_state.py)
│   ├── cert.py               #    cert TLS, réseau (ex deck_cert.py)
│   ├── http.py               #    DeckHTTPHandler + routes (ex deck_http.py)
│   ├── xplane.py             #    détection X-Plane (ex deck_xplane.py)
│   ├── installer.py          #    installation (ex deck_installer.py)
│   ├── flight.py             #    reprise de vol (ex deck_flight.py)
│   ├── instance.py           #    PID/kill (ex deck_instance.py)
│   ├── panel_i18n.py         #    PANEL_I18N (ex deck_panel_i18n.py)
│   └── runner.py             #    thread serveur (ex deck_runner.py)
│
├── static/                   # 🖥️ Ressources web
│   ├── index.html
│   ├── css/                  #    (déjà en place depuis P3)
│   │   ├── theme.css
│   │   ├── layout.css
│   │   ├── widgets.css
│   │   ├── responsive.css
│   │   └── modal.css
│   └── js/                   #    ← NOUVEAU dossier (aujourd'hui: static/*.js)
│       ├── main.js
│       ├── i18n.js
│       ├── state.js
│       ├── api.js
│       ├── ui.js
│       ├── config.js
│       ├── sliders.js
│       ├── compass.js
│       ├── vitals.js
│       ├── actions.js
│       ├── modal.js
│       ├── info.js
│       └── readme.js
│
├── data/                     # ⚙️ runtime (state.txt, prefs.json, panel.pid…)
├── certs/                    # 🔐 certificats générés
│
├── docs/                     # 📄 documentation (← NOUVEAU)
│   ├── readme_FR.md          #    (déplacés depuis la racine)
│   ├── readme_EN.md
│   └── CHANGELOG.md          #    (optionnel — actuellement géré à la main)
│
├── aerodev-yawrescue.html    # page vitrine — CONSERVÉE (décision utilisateur)
├── changelog.txt             # CONSERVÉ (géré à la main)
├── launcher.txt              # launcher
└── translations.lua          # script Lua source
```

**Principes de la cible :**
1. **Entry points à la racine** (`panel.py`, `server.py`, `start_panel.bat`) :
   le `.bat` vérifie leur présence dans le même dossier → ne jamais les déplacer.
2. **Logique Python dans un package `deck/`** au lieu de 10 fichiers plats
   `deck_*.py` : imports `from deck import state` plus propres, `__init__.py`
   centralise les ré-exports (compat avec l'existant pendant la migration).
3. **JS dans `static/js/`**, CSS dans `static/css/` : l'arborescence web reflète
   les types de ressources.
4. **Docs dans `docs/`**, runtime dans `data/`, certs dans `certs/`.

---

## 3. 🗺️ Migration des chemins — à cocher au fil du code

### 3.1 Python : `deck_*.py` → package `deck/`

⚠️ **Piège n°1 — `deck_paths.SCRIPT_DIR`** : aujourd'hui `Path(__file__).parent`.
Déplacé dans `deck/paths.py`, il doit devenir **`Path(__file__).resolve().parent.parent`**
(sinon `STATIC_DIR`/`DATA_DIR` pointeront dans `deck/`).

⚠️ **Piège n°2 — imports relatifs dans le package** : à l'intérieur de `deck/`,
les modules s'importent entre eux (`deck_http` → `deck_cert`, `deck_state`…).
En package, préférer les imports **absolus** `from deck.cert import …`.

| Chemin actuel (racine) | Chemin cible (package) | Imports à modifier | Statut |
|---|---|---|---|
| `deck_paths.py` | `deck/paths.py` | `from deck_paths import …` → `from deck.paths import …` ; **SCRIPT_DIR → parent.parent** | [ ] |
| `deck_log.py` | `deck/log.py` | `from deck_log import …` → `from deck.log import …` | [ ] |
| `deck_prefs.py` | `deck/prefs.py` | `from deck_prefs import …` → `from deck.prefs import …` | [ ] |
| `deck_state.py` | `deck/state.py` | `from deck_state import …` → `from deck.state import …` | [ ] |
| `deck_cert.py` | `deck/cert.py` | `from deck_cert import …` → `from deck.cert import …` | [ ] |
| `deck_http.py` | `deck/http.py` | `from deck_http import …` → `from deck.http import …` | [ ] |
| `deck_xplane.py` | `deck/xplane.py` | `from deck_xplane import …` → `from deck.xplane import …` | [ ] |
| `deck_installer.py` | `deck/installer.py` | `from deck_installer import …` → `from deck.installer import …` | [ ] |
| `deck_flight.py` | `deck/flight.py` | `from deck_flight import …` → `from deck.flight import …` | [ ] |
| `deck_instance.py` | `deck/instance.py` | `from deck_instance import …` → `from deck.instance import …` | [ ] |
| `deck_panel_i18n.py` | `deck/panel_i18n.py` | `from deck_panel_i18n import …` → `from deck.panel_i18n import …` | [ ] |
| `deck_runner.py` | `deck/runner.py` | `import deck_runner` → `from deck import runner` (panel.py) | [ ] |
| — | `deck/__init__.py` | **à créer** : ré-exporter les noms publics (compat `panel.py`/`server.py` tant qu'ils ne sont pas migrés) | [ ] |

**Fichiers qui référencent ces modules (à mettre à jour dans le même mouvement) :**
- `panel.py` : `import deck_runner`, `from deck_flight import …`, `from deck_installer import …`, `from deck_instance import …`, `from deck_panel_i18n import …`, `from deck_xplane import …`
- `server.py` : `from deck_paths import …`, `from deck_log import …`, `from deck_prefs import …`, `from deck_state import …`, `from deck_cert import …`, `from deck_http import …`
- Les imports **internes au package** : `deck_http` → `deck_cert`/`deck_flight`/`deck_installer`/`deck_log`/`deck_paths`/`deck_prefs`/`deck_state` ; `deck_prefs` → `deck_paths` ; `deck_runner` → `deck_paths` ; `deck_state` → `deck_paths` ; `deck_instance` → `deck_paths` ; `deck_flight` → `deck_paths`.

✅ Vérif après migration PY : `python -m py_compile *.py deck/*.py` ;
`python -c "import panel, server"` (aucun nom manquant) ;
serveur relancé → baseline P0.

---

### 3.2 JS/CSS : `static/*.js` → `static/js/`

⚠️ **Piège — les URL `/api/*`** (`fetch('/api/state')` dans state.js, `fetch('/api/prefs')`
dans i18n.js…) **ne changent pas** : ce sont des chemins HTTP servis par
`deck_http.py`, pas des chemins de fichiers. Seules les balises `<script src>`
d'`index.html` changent.

| Chemin actuel | Chemin cible | Référence à modifier | Statut |
|---|---|---|---|
| `static/modal.js` | `static/js/modal.js` | `index.html` : `src="modal.js?v=1"` → `src="js/modal.js?v=1"` | [ ] |
| `static/info.js` | `static/js/info.js` | `index.html` : `src="info.js?v=3"` → `src="js/info.js?v=3"` | [ ] |
| `static/readme.js` | `static/js/readme.js` | `index.html` : `src="readme.js?v=3"` → `src="js/readme.js?v=3"` | [ ] |
| `static/config.js` | `static/js/config.js` | `index.html` : `src="config.js?v=2"` → `src="js/config.js?v=2"` | [ ] |
| `static/i18n.js` | `static/js/i18n.js` | `index.html` : `src="i18n.js?v=3"` → `src="js/i18n.js?v=3"` | [ ] |
| `static/state.js` | `static/js/state.js` | `index.html` : `src="state.js?v=2"` → `src="js/state.js?v=2"` | [ ] |
| `static/api.js` | `static/js/api.js` | `index.html` : `src="api.js?v=2"` → `src="js/api.js?v=2"` | [ ] |
| `static/sliders.js` | `static/js/sliders.js` | `index.html` : `src="sliders.js?v=2"` → `src="js/sliders.js?v=2"` | [ ] |
| `static/ui.js` | `static/js/ui.js` | `index.html` : `src="ui.js?v=3"` → `src="js/ui.js?v=3"` | [ ] |
| `static/compass.js` | `static/js/compass.js` | `index.html` : `src="compass.js?v=3"` → `src="js/compass.js?v=3"` | [ ] |
| `static/vitals.js` | `static/js/vitals.js` | `index.html` : `src="vitals.js?v=2"` → `src="js/vitals.js?v=2"` | [ ] |
| `static/actions.js` | `static/js/actions.js` | `index.html` : `src="actions.js?v=2"` → `src="js/actions.js?v=2"` | [ ] |
| `static/main.js` | `static/js/main.js` | `index.html` : `src="main.js?v=2"` → `src="js/main.js?v=2"` | [ ] |

✅ Vérif après migration JS : `node --check static/js/*.js` ; serveur relancé →
`/` répond, chaque `/js/*.js` et `/css/*.css` en **200** ; page affichée sans
erreur console (ordre de chargement des scripts inchangé).

---

### 3.3 Docs : `readme_*.md` → `docs/`

| Chemin actuel | Chemin cible | Référence à vérifier | Statut |
|---|---|---|---|
| `readme_FR.md` | `docs/readme_FR.md` | aucune référence code (docs seules) — le `.bat` n'y fait pas référence | [ ] |
| `readme_EN.md` | `docs/readme_EN.md` | idem | [ ] |

> ⚠️ `start_panel.bat` vérifie **seulement** la présence de `panel.py` et
> `server.py` au même endroit que lui → les entrées restent à la racine, aucune
> retouche du `.bat` nécessaire pour les étapes 3.1–3.3.

---

## 4. ✅ Bugs corrigés (B1 → B8)

| Bug | Localisation | Correctif appliqué |
|---|---|---|
| **B1** | `panel.py:31` | `XPLANE_PROCESS_NAMES` : doublon `"X-Plane.exe"` supprimé ; constante désormais parcourue par `is_xplane_running()` |
| **B2** | `panel.py:1091,1099` | statuts d'installation codés en dur FR → clés `install_downloading` / `install_copying_files` de `PANEL_I18N` (FR/EN) |
| **B3** | `static/ui.js:109` | fallback « Aucun avion détecté » → clé i18n `telemetry.no_aircraft` |
| **B4** | `info.js:233`, `readme.js:107` | variables mortes `currentInfoKey` / `readmeModalOpen` supprimées (+ fermeture `Escape` ajoutée à la modale Readme) |
| **B5** | `index.html:624` | texte source EN → `Aucun avion détecté` (langue par défaut = fr) |
| **B6** | `index.html` (6×) | SVG ⓘ dupliqué → `<symbol id="icon-info">` unique + 6 `<use>` |
| **B7** | `server.py:167` | `dlog()` réactivé derrière `DEBUG_LOGGING` (env `YAW_RESCUE_DEBUG=1` ou `--debug`) |
| **B8** | `panel.py:1212` | `os._exit(0)` documenté, protégé contre les doubles appels, flush avant sortie |

---

## 5. Ce qui est modifiable, par fichier

### `panel.py` — GUI Tkinter (644 l., P2 ✅)
- **Constantes GUI** : couleurs `BG`, `ACCENT`, `DANGER`…, tailles de fenêtre
  (`420×750`), polices (`"Segoe UI"`, `"Cascadia Code"`), couleurs
  `activebackground`.
- **Boucles** : `_check_server` (1 000 ms), `_check_xplane` (3 000 ms).
- **Ports** `main()` : `--port 8443`, `--cert-port 8080`, `--no-cert`.
- Détection/installation/reprise de vol → modules `deck_*` (§3.1).

### `server.py` — serveur HTTP (263 l., P1 ✅)
- Ré-exports des noms publics (compat `import server as srv`).
- Bootstrap d'auto-install pip ; `DeckHTTPServer` ; `state_watcher` (0,1 s) ; `main()`.

### `static/index.html` — page web (484 l., P4.1 ✅ + P4.2 ✅)
- Structure 3 onglets ; modales ⓘ / À propos.
- ⚠️ **C'est ici que se font les modifications de chemins §3.2** (balises
  `<script src>` et `<link href>`).

### `static/css/*` — 5 feuilles (P3 ✅)
- **Palette complète** : `:root` dans `theme.css` (`--bg-primary`, `--accent`…).
- Breakpoints dans `responsive.css`.
- ⚠️ **Ordre des `<link>` dans index.html = ordre de cascade** — à préserver.

### Modules JS `static/*.js` (→ `static/js/` §3.2)
- `config.js` : `CONFIG_CARDS` (6 cartes), `POLL_INTERVAL=150 ms`,
  `COMMAND_DEBOUNCE=200 ms`.
- `state.js` : `RECONNECT_INTERVAL=2000`, `LOCAL_CHANGE_GUARD_MS=2000`.
- `vitals.js` : `GEAR_ALERT_ALT_FT=1000`.
- `ui.js` : `updateUI()`, `buildSliderMaps()`, onglets (localStorage `ayd-tab`).
- `i18n.js` : dictionnaire FR/EN complet.
- `info.js` / `readme.js` / `modal.js` : contenus d'aide + modales communes (P5.1 ✅).
- `compass.js` : rose générée par `buildCompassRose()` (P4.1 ✅).

### Autres
- `deck_*.py` : constantes de détection, installation, vols → §3.1 (migration) et
  leur contenu décrit en §1.
- `aerodev-yawrescue.html` : page vitrine **conservée** (décision utilisateur).
- `changelog.txt` : **géré à la main** (décision utilisateur).

---

## 6. 🧭 Feuille de route

| Phase | Objet | Statut |
|---|---|---|
| P0 | Filet de sécurité (baseline, compile) | à rejouer avant/après chaque phase |
| P1 | Découper `server.py` → 6 modules `deck_*` | ✅ 977 → 263 l. |
| P2 | Découper `panel.py` → 6 modules `deck_*` | ✅ 1 324 → 644 l. |
| P3 | Découper `style.css` → 5 feuilles | ✅ 1 186 l. découpées |
| P4.1 | Boussole SVG générée en JS | ✅ index.html −56 l. |
| P4.2 | Cartes Config rendues par données | ✅ index.html −144 l. |
| P4.3 | Fragments HTML | ❌ non requis |
| P5.1 | Module `modal.js` commun | ✅ info.js 257 / readme.js 130 |
| P5.2 | Alléger `ui.js` | [ ] optionnel |
| P6 | Fichiers morts / changelogs | ✅ **annulée par l'utilisateur** (page vitrine + `changelog.txt` conservés) |
| P7 | Contrôle final & docs | ✅ **P7 docs fait** (readmes à jour : structure deck/, static/js/, docs/, flag --debug) |
| **P8** | **Migration arborescence (§3)** | ✅ **terminée** (P8.1→P8.4) |

### P8 — Migration de l'arborescence (nouvelle)

**Étape P8.1 — package Python `deck/` (§3.1) — ✅ terminé :**
- [x] Créé `deck/` + `deck/__init__.py` (imports des 12 sous-modules + ré-exports
      publics : `DeckHTTPHandler`, `PANEL_I18N`, `DEFAULT_STATE`, `get_local_ip`…).
- [x] Les 12 `deck_*.py` vivent maintenant dans `deck/` (préfixe retiré :
      `deck_paths.py` → `deck/paths.py`, …). Anciens fichiers racine supprimés.
- [x] `deck/paths.py` : `SCRIPT_DIR = Path(__file__).resolve().parent.parent`
      (le piège n°1) — docstring mise à jour (`deck.state / deck.prefs / …`).
- [x] Imports internes réécrits : `from deck_…` → `from deck.…` (15 occurrences)
      + racine : `panel.py` (`from deck import runner`, `from deck.flight import …`),
      `server.py` (7 lignes `from deck.… import …`).
- [x] `panel.py` : usages `deck_runner.…` → `runner.…` (9 occurrences).
✅ Vérifs passées : `py_compile` panel/server/deck/* ; `import panel, server` OK ;
`from deck import DeckHTTPHandler, PANEL_I18N, DEFAULT_STATE, get_local_ip` OK ;
baseline P0 rejouée → `/`, `/index.html`, `/api/health`, `/api/prefs`,
`/api/state`, `/api/info`, `/api/install-status` = **200** ; `<title>Yaw Rescue</title>`.

**Étape P8.2 — JS dans `static/js/` (§3.2) — ✅ terminé :**
- [x] Créé `static/js/` ; les 13 `.js` y ont été déplacés
      (modal, info, readme, config, i18n, state, api, sliders, ui, compass,
      vitals, actions, main). `static/` ne contient plus que `css/`, `js/`,
      `index.html`.
- [x] Les 13 `<script src>` d'`index.html` ont reçu le préfixe `js/`
      (`src="js/modal.js?v=1"`…). ⚠️ Le sed `[a-z]*` raté `i18n.js` (chiffre) →
      corrigé manuellement.
✅ Vérifs passées : `node --check static/js/*.js` (13 fichiers) ; serveur relancé →
les 13 `/js/*.js` = **200** ; page servie avec 13 `src="js/` ; `/index.html` = 200.
Les `fetch('/api/*')` (state.js, i18n.js, ui.js…) inchangés (chemins HTTP, pas fichiers).

**Étape P8.3 — docs dans `docs/` (§3.3) — ✅ terminé :**
- [x] Créé `docs/` ; `readme_FR.md` (16,7 Ko) et `readme_EN.md` (15 Ko)
      déplacés depuis la racine.
✅ Vérifs passées : grep `readme_FR|readme_EN` dans .py/.bat/.js/.html → aucune
référence cassée (docs seules). ⚠️ Deux sauvegardes manuelles `readme_FR copy.md` /
`readme_EN copy.md` (strictement identiques aux originaux) traînent encore à la
racine — à supprimer à la main si elles ne servent plus.

**Étape P8.4 — contrôle final — ✅ terminé :**
- [x] `py_compile` panel/server/deck/* + `node --check static/js/*.js` : zéro erreur.
- [x] Baseline P0 rejouée : `/`, `/api/health`, `/api/state`, `/js/main.js`,
      `/js/i18n.js`, `/css/theme.css` = **200**.
- [x] **Validation utilisateur réelle** : reload X-Plane + refresh complet côté JS
      → tout est OK (conditions réelles, panneau + web).
- [x] `start_panel.bat` : inchangé (entry points `panel.py`/`server.py` toujours
      à la racine — pas de retouche nécessaire).
- [x] Ce document mis à jour avec la structure finale (§2).

---

## 7. 🎯 Synthèse des chantiers restants

1. **P8 — migration arborescence** ✅ : package `deck/`, `static/js/`, `docs/` —
   **terminée et validée en conditions réelles** (reload X-Plane + refresh JS).
2. **P5.2 — alléger `ui.js`** (optionnel) : déléguer davantage à compass/vitals/
   sliders.
3. **P7 — docs** ✅ : `docs/readme_FR.md` / `docs/readme_EN.md` mis à jour
   (arborescence `deck/` + `static/{css,js}` + `docs/`, option `--debug` / env
   `YAW_RESCUE_DEBUG=1` dans les tableaux d'options).
4. **Nettoyage manuel proposé** : supprimer `readme_FR copy.md` / `readme_EN copy.md`
   à la racine (sauvegardes identiques aux originaux — à valider).
5. **GUI `python panel.py`** : ouverture de la fenêtre Tkinter à valider sur un
   poste avec session graphique (non testable ici).
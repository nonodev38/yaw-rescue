# yaw-rescue
“Yaw Rescue – Répare le yaw instable des joysticks (X‑Plane 11/12, FlyWithLua + Python)”

# yaw-rescue
“Yaw Rescue – Répare le yaw instable des joysticks (X‑Plane 11/12, FlyWithLua + Python)”

================================================================================
  YAW RESCUE - Installation / Installation
================================================================================

English below / Francais ci-dessous

================================================================================
  ENGLISH
================================================================================

  FILE PLACEMENT
  --------------

  Your FlyWithLua Scripts folder must look like this:

    X-Plane/Resources/plugins/FlyWithLua/Scripts/
    +-- auto_yaw.lua                    <-- Main script (FlyWithLua)
    +-- auto_yaw_deck.lua               <-- Bridge to Python server
    +-- AutoYaw_profiles.cfg            <-- Created automatically
    +-- Auto Yaw Deck/                  <-- Python server + web app
        +-- panel.py
        +-- server.py
        +-- translations.lua
        +-- start_panel.bat
        +-- static/
        +-- data/                       <-- Created automatically
        +-- certs/                      <-- Created automatically

  IMPORTANT
  ---------

  1. auto_yaw.lua and auto_yaw_deck.lua MUST be directly in Scripts/
     (FlyWithLua only loads scripts from the root Scripts/ folder)

  2. The "Auto Yaw Deck" folder MUST stay inside Scripts/

  3. Do NOT move auto_yaw_deck.lua into "Auto Yaw Deck/"

  QUICK START
  -----------

  1. Copy these 3 items into Scripts/:
     - auto_yaw.lua
     - auto_yaw_deck.lua
     - Auto Yaw Deck/

  2. Start X-Plane

  3. Double-click "Auto Yaw Deck/start_panel.bat"

  4. Scan the QR code with your phone

  5. Accept the SSL certificate warning

  6. Done! Adjust settings from your smartphone.

  TROUBLESHOOTING
  ---------------

  - Script not loading: check Files are in Scripts/ root, not in subfolder
  - Server won't start: python --version (needs 3.7+), packages auto-install
  - Phone can't connect: same WiFi, accept SSL, or install CA cert

================================================================================
  FRANCAIS
================================================================================

  PLACEMENT DES FICHIERS
  ----------------------

  Votre dossier Scripts de FlyWithLua doit ressembler a ceci :

    X-Plane/Resources/plugins/FlyWithLua/Scripts/
    +-- auto_yaw.lua                    <-- Script principal (FlyWithLua)
    +-- auto_yaw_deck.lua               <-- Pont vers le serveur Python
    +-- AutoYaw_profiles.cfg            <-- Cree automatiquement
    +-- Auto Yaw Deck/                  <-- Serveur Python + application web
        +-- panel.py
        +-- server.py
        +-- translations.lua
        +-- start_panel.bat
        +-- static/
        +-- data/                       <-- Cree automatiquement
        +-- certs/                      <-- Cree automatiquement

  IMPORTANT
  ---------

  1. auto_yaw.lua et auto_yaw_deck.lua DOIVENT etre directement dans Scripts/
     (FlyWithLua ne charge que les scripts a la racine de Scripts/)

  2. Le dossier "Auto Yaw Deck" DOIT rester dans Scripts/

  3. NE deplacez PAS auto_yaw_deck.lua dans "Auto Yaw Deck/"

  DEMARRAGE RAPIDE
  ----------------

  1. Copiez ces 3 elements dans Scripts/ :
     - auto_yaw.lua
     - auto_yaw_deck.lua
     - Auto Yaw Deck/

  2. Demarrez X-Plane

  3. Double-cliquez sur "Auto Yaw Deck/start_panel.bat"

  4. Scannez le QR code avec votre telephone

  5. Acceptez l'avertissement du certificat SSL

  6. C'est fait ! Ajustez les parametres depuis votre smartphone.

  DEPANNAGE
  ---------

  - Script ne se charge pas : verifiez que les fichiers sont a la racine de Scripts/
  - Serveur ne demarre pas : python --version (besoin de 3.7+), les packages s'installent auto
  - Telephone ne se connecte pas : meme WiFi, acceptez le SSL, ou installez le certificat CA

================================================================================



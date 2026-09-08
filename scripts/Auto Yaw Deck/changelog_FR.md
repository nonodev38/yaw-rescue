# Yaw Rescue v1.0.3 — Notes de version X-Plane.org

> Copiez-collez les trois sections ci-dessous sur votre page de téléchargement X-Plane.org
> (texte brut, sans Markdown — le forum supprime la mise en forme).

---

## Détails de la nouvelle version

Yaw Rescue v1.0.3 — une mise à jour de stabilité critique qui corrige les erreurs de chargement des scripts Lua, améliore la détection de l'état d'X-Plane, ajoute le lancement d'X-Plane depuis le web avec reprise au dernier aéroport, et complète la traduction FR/EN de tous les éléments de l'interface. Cette version résout le problème des « scripts mis en quarantaine » qui empêchait le plugin de fonctionner sur FlyWithLua NXT 2.8.16.

---

## Quoi de neuf

1. CORRECTIONS DES SCRIPTS LUA — COMPATIBILITÉ FLYWITHLUA NXT 2.8.16
   - Correction de 4 erreurs de dataref qui provoquaient la mise en quarantaine des scripts à chaque chargement :
     a. Remplacement de dataref_table() par dataref() pour les datarefs de type string (sim/aircraft/view/acf_descrip et sim/aircraft/present/acf_file — ce dernier n'existe plus dans XP12).
     b. Remplacement du dataref obsolète sim/cockpit2/controls/flap_ratio par sim/cockpit2/controls/flap_handle_request_ratio (writable).
     c. Remplacement du dataref obsolète sim/flightmodel/position/magpsi par sim/flightmodel/position/mag_psi.
   - Les scripts se chargent maintenant sans erreur sur FlyWithLua NXT 2.8.16+.

2. LANCEMENT D'X-PLANE DEPUIS LE WEB AVEC REPRISE AU DERNIER AÉROPORT
   - Le bouton « Lancer X-Plane depuis le PC » sur la page de connexion réutilise la même logique de reprise au dernier aéroport que le panneau de contrôle Python.
   - Lit le dernier aéroport et la dernière piste depuis Freeflight.prf (avec fallback sur log.txt), lit le dernier avion, écrit data/flight.json, et lance X-Plane.exe --new_flight_json=... — un clic pour reprendre votre vol.

3. AMÉLIORATION DE LA DÉTECTION DE L'ÉTAT D'X-PLANE
   - La vérification du processus est maintenant mise en cache (TTL de 1 seconde) pour éviter d'appeler tasklist 10 fois par seconde.
   - Période de grâce : si le processus était actif et que tasklist indique qu'il s'est arrêté, un tick supplémentaire est accordé avant de confirmer l'état « off ».
   - Nouvelle heuristique : si le processus tourne mais que state.txt a plus de 10 secondes, l'état est « loading » (couvre l'ouverture du menu, le chargement d'un avion ou la pause) au lieu de « ready » ou « off ».
   - Nouvelle fonction _log_file_recently_modified() qui détecte le démarrage d'X-Plane même avant que le bridge Lua écrive state.txt.

4. CORRECTIONS DU BOUTON DE LA PAGE DE CONNEXION
   - Le bouton « Lancer X-Plane » ne clignote plus pendant le démarrage d'X-Plane (flag launchPending qui empêche setConnected de le réafficher).
   - Le texte du bouton n'est réinitialisé que lorsqu'il devient visible, pas pendant la phase de lancement.
   - Le texte du bouton est correctement traduit lors du changement de langue et du rafraîchissement de la page.

5. TRADUCTION FR/EN COMPLÈTE
   - Ajout des clés i18n manquantes : diagram.flaps, diagram.flaps_sub, diagram.pitch, diagram.pitch_sub, diagram.roll, diagram.roll_sub, diagram.yaw, diagram.yaw_sub, connect.support.
   - Tout le texte de l'interface bascule correctement entre le français et l'anglais.

6. JOURNAL DE DÉBOGAGE
   - Nouveau fichier data/debug_state.txt écrit à chaque interrogation de l'état, affichant : xplane_active, xplane_state, timestamp age, process_running, log_loading, log_recently_modified.
   - Utile pour le diagnostic des problèmes de détection d'état.

7. CACHE BUSTING
   - Toutes les références JS et CSS dans index.html incluent maintenant le paramètre ?v=3 pour forcer le rafraîchissement du cache du navigateur après les mises à jour.

---

## Prérequis

- X-Plane 11 ou 12 (Windows / macOS / Linux)
- Plugin FlyWithLua NXT (Resources/plugins/FlyWithLua)
- Python 3.7+ avec tkinter (pour le panneau de contrôle GUI)
- Un smartphone sur le même réseau WiFi que le PC
- Les packages Python requis (cryptography, qrcode) sont installés automatiquement au premier lancement
- Note : la « reprise au dernier aéroport » nécessite X-Plane 12.4+

---

*Fichier : Yaw_Rescue_v1.0.3.zip — version 1.0.3*

---

# Yaw Rescue v1.0.2 — Notes de version X-Plane.org

> Copiez-collez les trois sections ci-dessous sur votre page de téléchargement X-Plane.org
> (texte brut, sans Markdown — le forum supprime la mise en forme).

---

## Détails de la nouvelle version

Yaw Rescue v1.0.2 — une mise à jour majeure par rapport à la version initiale v1.0.0. Cette version ajoute un ensemble complet d'instruments de vol en direct autour de la boussole, une alerte de rétraction des volets, la possibilité de reprendre directement au dernier aéroport, un lanceur plus intelligent et plusieurs améliorations de l'interface. L'application web a également été refactorisée en modules dédiés pour une maintenance plus facile. Voir « Quoi de neuf » ci-dessous pour la liste complète.

---

## Quoi de neuf

1. INSTRUMENTS DE VOL EN DIRECT AUTOUR DE LA BOUSSOLE
   - Bande de train d'atterrissage au-dessus de la boussole : une cellule par train (N / L / R), chacune affichant DN / UP / MID en direct.
   - RPM moteur et Throttle à gauche de la boussole.
   - Vitesse verticale (FPM) et Angle d'attaque (AOA) à droite de la boussole.
   - Chaque valeur est codée par couleur de manière interactive : train (vert/orange/rouge), throttle (vert jusqu'à 70%, orange jusqu'à 90%, rouge au-delà), FPM (vert au-dessus de -400, rouge au-delà de -1000), AOA (vert en dessous de 12°, orange jusqu'à 16°, rouge au-dessus — approche de décrochage).
   - Alerte de configuration d'atterrissage : la bande de train entière clignote en rouge lorsque tout train n'est pas complètement sorti en dessous de 1000 pieds, ou lorsque l'alerte volets est active.
   - Avions multi-moteurs : RPM et throttle affichent la valeur la plus élevée sur tous les moteurs.

2. ALERTE DE RÉTRACTION DES VOLETS
   - Utilise la vitesse maximale volets sortis (Vfe) de l'avion depuis X-Plane. Lorsque la vitesse atteint Vfe alors que les volets sont encore sortis, la section Volets pulse en rouge et le badge de position clignote — même lorsque la section est réduite. L'hystérésis empêche le scintillement près du seuil.

3. REPRISE AU DERNIER AÉROPORT
   - Le panneau de contrôle lit le dernier aéroport (et piste) depuis les propres données d'X-Plane (Freeflight.prf, avec log.txt comme fallback).
   - Un clic sur « Démarrer X-Plane » lance le simulateur directement à cet aéroport avec votre dernier avion — sans passer par les menus (nécessite X-Plane 12.4+ ; sur les versions plus anciennes, le simulateur démarre normalement). Case à cocher optionnelle pour désactiver.

4. LANCEUR WINDOWS PLUS INTELLIGENT
   - start_panel.bat détecte maintenant automatiquement un Python fonctionnel (py -3 / python / python3, vérification de version), vérifie tkinter, avertit si le port 8443 est déjà utilisé, et affiche des instructions de correction claires si quelque chose manque.

5. AMÉLIORATIONS DE L'INTERFACE
   - Section Volets retravaillée : maintenant au-dessus de la section tangage, diagramme compact, réductible (état mémorisé par appareil), badge de position en direct et boutons prédéfinis qui se mettent en surbrillance automatiquement sur la position actuelle.
   - L'onglet actif (Config / Controls / Telemetry) est mémorisé par appareil.
   - La préférence de langue (FR/EN) est sauvegardée côté serveur, elle survit aux redémarrages d'X-Plane et aux changements d'IP et est partagée par tous les appareils.

6. MAINTENANCE
   - Code de l'application web réorganisé en modules dédiés (pas de changement fonctionnel).
   - Correction d'une erreur de syntaxe de génération de certificat qui pouvait empêcher le démarrage du serveur.

---

## Prérequis

- X-Plane 11 ou 12 (Windows / macOS / Linux)
- Plugin FlyWithLua NXT (Resources/plugins/FlyWithLua)
- Python 3.7+ avec tkinter (pour le panneau de contrôle GUI)
- Un smartphone sur le même réseau WiFi que le PC
- Les packages Python requis (cryptography, qrcode) sont installés automatiquement au premier lancement
- Note : la « reprise au dernier aéroport » nécessite X-Plane 12.4+

---

*Fichier : Yaw_Rescue_v1.0.2.zip — version 1.0.2*

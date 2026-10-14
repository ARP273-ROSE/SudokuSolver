# Changelog

## 1.3.0 — 14 octobre 2026

- **Apparence figée** : style Fusion, palette complète (états désactivés compris) et police
  Source Sans 3 embarquée (`polices/`, licence OFL) — l'interface ne change plus avec le thème
  clair/sombre ni avec les polices du système ; la grille utilise la même police.
- **Vrai explorateur de fichiers** pour Ouvrir et Enregistrer sous Linux : boîte Qt complète
  (barre latérale avec dossier personnel, Bureau, Documents, supports montés…) au lieu de la
  boîte réduite du portail ; Windows et macOS gardent la leur (`interface_kit.py`, kit commun).
- **Manuel PDF** français et anglais au format maison, avec captures réelles, ouvert par
  *Aide > Manuel (PDF)* (F1) ; sources `docs/src/`, captures `docs/captures.py`, compilation
  `docs/src/compiler.py`. Il remplace l'ancien `manuel.pdf` bilingue, dont les passages sur
  l'installation, les réglages et les rapports étaient périmés.
- **Logo** : une seule source, `logo.svg`, rendue par `make_logo.py` en PNG 16 à 512, `.ico`
  (Windows) et `.icns` (macOS) ; affiché dans *À propos* et sur la couverture du manuel.
  `generate_logo.py` (Pillow) est retiré.
- Le nom de la technique la plus difficile, dans la barre d'état, est traduit.
- Tests : vrai démarrage du programme, style figé, présence des manuels, clés des techniques.

## 1.2.0 — 14 octobre 2026

- **macOS et Linux** : image disque `.dmg` (Apple Silicon et Intel) et archive `.tar.gz`
  (x86_64 et ARM64) avec `installer.sh` (installation dans le profil, entrée de menu, sans
  sudo), construites par le même et unique workflow que l'installeur Windows (`release.yml`,
  sur tag `vX.Y.Z`) ; lien permanent `releases/latest/download/SudokuSolver-Setup.exe`.
- **Mise à jour automatique** sur les trois systèmes (kit commun, `updater.py`) : au démarrage
  et par *Aide > Rechercher des mises à jour* ; adresse vérifiée (GitHub uniquement), notes de
  version dans la langue de l'interface.
- **Rapports de problème** : accord demandé au premier lancement, *Aide > Signaler un
  problème*, envoi automatique réglable dans le menu *Aide*.
- L'installeur Windows efface l'ancienne version et détecte l'application ouverte (verrou
  nommé `SudokuSolverEnCours`).
- Journal et rapports de plantage hors du dossier d'installation (ils y étaient écrits, et la
  mise à jour les aurait effacés) ; ouverture et enregistrement de grilles proposés dans le
  dossier personnel.
- Langue : celle du système au premier lancement (détection corrigée sous Windows,
  « French_France »), puis celle choisie dans le menu *Langue*, désormais retenue.
- Derniers textes en anglais seulement traduits (erreurs, fichier trop volumineux, fenêtre de
  plantage, filtres de fichiers).
- Tests : moteur, textes affichés en dur et clés de traduction, interface sous Xvfb, cohérence
  du kit, lancés par la CI (`tests.yml`, qui reprend le garde-fou de confidentialité).
- Retrait des mentions personnelles ; éditeur de l'installeur et organisation Qt = ARP273-ROSE (aucun réglage n'en dépendait).
- Garde-fou `tests/test_confidentialite.py` (fichiers, texte des PDF, PNG, binaires), lancé par la CI.

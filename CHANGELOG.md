# Changelog

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

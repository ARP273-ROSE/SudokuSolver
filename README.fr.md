# SudokuSolver

*English version: [README.md](README.md).*

**Solveur, générateur et tuteur de sudoku, en français et en anglais** : il
résout n'importe quelle grille, en génère de nouvelles par niveau de
difficulté, et explique pas à pas les techniques pour les résoudre soi-même
(singletons nus et cachés, paires, triplets, pointage, réduction
ligne/boîte, X-Wing).

L'interface suit la langue du système au premier lancement, puis celle
choisie dans le menu *Langue*, qui est retenue.

## Télécharger

Paquets prêts à l'emploi, Python compris, sur la
[page des versions](https://github.com/ARP273-ROSE/SudokuSolver/releases/latest) :

| Système | Fichier |
|---|---|
| Windows | `SudokuSolver-Setup.exe` — lien permanent : [dernier installeur](https://github.com/ARP273-ROSE/SudokuSolver/releases/latest/download/SudokuSolver-Setup.exe) |
| macOS (Apple Silicon / Intel) | `SudokuSolver-X.Y.Z-macos-arm64.dmg` / `-macos-x86_64.dmg` |
| Linux (x86_64 / ARM64) | `SudokuSolver-X.Y.Z-linux-x86_64.tar.gz` / `-linux-arm64.tar.gz`, puis `./installer.sh` |

Aucun droit d'administrateur n'est demandé. Le journal et les rapports vivent
hors du dossier d'installation et survivent aux mises à jour.

- **Windows** peut afficher « Windows a protégé votre ordinateur » au premier
  lancement (installeur non signé) : *Informations complémentaires*, puis
  *Exécuter quand même*.
- **macOS** : glisser l'application dans Applications, puis la première fois
  *clic droit > Ouvrir*.
- **Linux** : décompresser l'archive et lancer `./installer.sh` (installation
  dans `~/.local/share`, entrée de menu, sans sudo).

## Mises à jour et rapports de problème

Installée, l'application cherche une nouvelle version au démarrage et sur
demande (*Aide > Rechercher des mises à jour*), la télécharge depuis GitHub et
redémarre, sur les trois systèmes.

Au premier lancement, elle demande l'accord pour envoyer automatiquement un
court rapport technique en cas de plantage ou de gel. Ce choix se modifie dans
le menu *Aide*, où *Signaler un problème* permet aussi d'écrire un signalement.

## Utilisation

- **Cliquer** une case (ou les flèches) et taper **1 à 9** ; **0 / Suppr /
  Retour arrière** pour effacer.
- Choisir une difficulté puis **Nouvelle grille**.
- **Indice** montre et explique la prochaine étape logique ; **Étape
  suivante** l'applique.
- **Vérifier** compare les saisies à la solution ; **Résoudre** la donne.

Guide des techniques : `guide_techniques.pdf`. Le **manuel** (PDF, français et anglais) s'ouvre par *Aide > Manuel (PDF)* (F1).

L'apparence est figée (style Fusion, palette et police embarquées) : elle ne change pas avec le thème clair ou sombre du système. Ouvrir et Enregistrer passent par un explorateur de fichiers complet, y compris sous Linux.

## Depuis les sources

```bash
pip install -r requirements.txt
python main.py
```

Ou `launch.bat` (Windows) / `./launch.sh` (Linux, macOS), qui préparent un
environnement virtuel. Tests : `python -m pytest -q tests/` (interface sous
`xvfb-run` sous Linux).

## Licence

MIT

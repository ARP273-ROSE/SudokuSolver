"""Bilingual help dialogs: how-to-play and techniques catalogue."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from i18n import T, get_language


HOWTO_EN = """
<h2>How to play</h2>
<p>Fill every row, every column, and every 3×3 box with the digits 1 through 9,
without repeating any digit in a row, column, or box.</p>

<h3>Controls</h3>
<ul>
  <li><b>Click</b> a cell to select it, or use the <b>arrow keys</b> to move.</li>
  <li>Type <b>1</b>–<b>9</b> to fill the selected cell.</li>
  <li>Press <b>0</b>, <b>Delete</b>, <b>Backspace</b>, or <b>Space</b> to clear it.</li>
  <li><b>Given</b> digits (from the puzzle) are in black and cannot be edited.</li>
  <li>Your entries appear in <span style="color:#1f4d80">blue</span>; wrong entries (after <i>Check</i>)
      appear in <span style="color:#c0392b">red</span>.</li>
</ul>

<h3>Toolbar</h3>
<ul>
  <li><b>New puzzle</b> — generate a fresh puzzle at the chosen difficulty.</li>
  <li><b>Solve</b> — fill in the complete solution instantly.</li>
  <li><b>Hint</b> — show the next logical step with an explanation.</li>
  <li><b>Next step</b> — apply the next logical step automatically.</li>
  <li><b>Check</b> — highlight any entries that contradict the solution.</li>
  <li><b>Pencil marks</b> — toggle the display of candidates in each empty cell.</li>
  <li><b>Reset</b> — restore the original puzzle.</li>
</ul>

<h3>Difficulty levels</h3>
<ul>
  <li><b>Easy</b> — 36–45 clues, solvable with naked/hidden singles only.</li>
  <li><b>Medium</b> — 30–35 clues, adds naked and hidden pairs.</li>
  <li><b>Hard</b> — 26–32 clues, requires pointing pairs and box/line reduction.</li>
  <li><b>Expert</b> — 22–28 clues, requires X-Wing or harder patterns.</li>
</ul>

<p>See the <b>Solving techniques</b> menu entry for a full illustrated guide.</p>
"""

HOWTO_FR = """
<h2>Comment jouer</h2>
<p>Remplissez chaque ligne, chaque colonne et chaque boîte 3×3 avec les chiffres 1 à 9,
sans jamais répéter un chiffre dans une ligne, une colonne ou une boîte.</p>

<h3>Commandes</h3>
<ul>
  <li><b>Cliquez</b> sur une case pour la sélectionner, ou utilisez les <b>flèches</b>.</li>
  <li>Tapez <b>1</b>–<b>9</b> pour remplir la case sélectionnée.</li>
  <li>Appuyez sur <b>0</b>, <b>Suppr</b>, <b>Retour arrière</b> ou <b>Espace</b> pour effacer.</li>
  <li>Les chiffres <b>imposés</b> (de la grille d'origine) sont en noir et ne peuvent pas être modifiés.</li>
  <li>Vos saisies apparaissent en <span style="color:#1f4d80">bleu</span> ; les erreurs (après <i>Vérifier</i>)
      apparaissent en <span style="color:#c0392b">rouge</span>.</li>
</ul>

<h3>Barre d'outils</h3>
<ul>
  <li><b>Nouvelle grille</b> — générer une nouvelle grille avec la difficulté choisie.</li>
  <li><b>Résoudre</b> — remplir la solution complète instantanément.</li>
  <li><b>Indice</b> — afficher la prochaine étape logique avec son explication.</li>
  <li><b>Étape suivante</b> — appliquer automatiquement la prochaine étape logique.</li>
  <li><b>Vérifier</b> — mettre en évidence les saisies qui contredisent la solution.</li>
  <li><b>Candidats</b> — afficher ou masquer les petits chiffres dans les cases vides.</li>
  <li><b>Réinitialiser</b> — restaurer la grille d'origine.</li>
</ul>

<h3>Niveaux de difficulté</h3>
<ul>
  <li><b>Facile</b> — 36–45 indices, résoluble avec singles nus/cachés uniquement.</li>
  <li><b>Moyen</b> — 30–35 indices, ajoute paires nues et paires cachées.</li>
  <li><b>Difficile</b> — 26–32 indices, requiert pointants et réduction ligne/boîte.</li>
  <li><b>Expert</b> — 22–28 indices, requiert X-Wing ou techniques plus avancées.</li>
</ul>

<p>Voir l'entrée de menu <b>Techniques de résolution</b> pour un guide illustré complet.</p>
"""

TECHNIQUES_EN = """
<h2>Solving techniques</h2>
<p>These techniques are listed from easiest to hardest. Each one eliminates
candidates or places a digit by pure logic — no guessing. Turn on
<b>Pencil marks</b> to see candidates while you practice.</p>

<h3>1. Naked Single</h3>
<p>If a cell has only one remaining candidate, that digit must go there.
It's the simplest move and every solver uses it constantly.</p>

<h3>2. Hidden Single</h3>
<p>If a digit can only go in one cell within a row, column, or box —
even when that cell still shows several candidates — place it.
This is how most easy puzzles get solved.</p>

<h3>3. Naked Pair</h3>
<p>If two cells in a unit have <i>the same two candidates</i> (and only those two),
those digits must occupy those two cells. Eliminate both digits from every
other cell of that unit.</p>

<h3>4. Hidden Pair</h3>
<p>If two digits can only appear in the same two cells of a unit,
those cells must contain exactly those two digits. Eliminate every other
candidate from both cells.</p>

<h3>5. Naked Triple</h3>
<p>Same as naked pair with three cells and three digits. The three cells
may not all have three candidates, but their combined candidates must be
exactly three digits.</p>

<h3>6. Pointing Pair / Triple</h3>
<p>If the only cells of a box that can contain a digit lie on one row
(or one column), the digit must go there — eliminate it from the rest of
that row (or column) outside the box.</p>

<h3>7. Box / Line Reduction</h3>
<p>The mirror of pointing: if a digit in a row (or column) is confined
to a single box, eliminate it from the rest of that box.</p>

<h3>8. X-Wing</h3>
<p>If two rows each restrict a digit to exactly the same two columns,
the digit forms a 2×2 rectangle. The digit must occupy two opposite
corners, so it can be eliminated from those two columns in every
other row. The pattern also works with rows and columns swapped.</p>

<h3>Beyond X-Wing</h3>
<p>Harder puzzles may require Swordfish, XY-Wing, colouring, or
Nishio — these are not yet implemented as hints but the internal
fast solver handles them via backtracking, so <b>Solve</b> always works.</p>
"""

TECHNIQUES_FR = """
<h2>Techniques de résolution</h2>
<p>Ces techniques sont classées de la plus simple à la plus avancée. Chacune
élimine des candidats ou place un chiffre par pure logique — sans deviner.
Activez les <b>Candidats</b> pour les voir pendant l'entraînement.</p>

<h3>1. Single nu (Naked Single)</h3>
<p>Si une case n'a plus qu'un seul candidat possible, ce chiffre y va forcément.
C'est le mouvement le plus simple et tout solveur l'applique en permanence.</p>

<h3>2. Single caché (Hidden Single)</h3>
<p>Si un chiffre ne peut se placer que dans une seule case d'une ligne,
colonne ou boîte — même si cette case a encore plusieurs candidats —
placez-le. La plupart des grilles faciles se résolvent ainsi.</p>

<h3>3. Paire nue (Naked Pair)</h3>
<p>Si deux cases d'une unité ont <i>exactement les deux mêmes candidats</i>
(et seulement ceux-là), ces deux chiffres occupent forcément ces deux cases.
Éliminez-les de toutes les autres cases de l'unité.</p>

<h3>4. Paire cachée (Hidden Pair)</h3>
<p>Si deux chiffres ne peuvent apparaître que dans les deux mêmes cases d'une unité,
ces cases contiennent forcément exactement ces deux chiffres. Éliminez tous les
autres candidats de ces deux cases.</p>

<h3>5. Triplet nu (Naked Triple)</h3>
<p>Comme la paire nue avec trois cases et trois chiffres. Les trois cases ne
contiennent pas forcément trois candidats chacune, mais l'union de leurs
candidats doit être exactement trois chiffres.</p>

<h3>6. Paire/Triplet pointant (Pointing)</h3>
<p>Si les seules cases d'une boîte pouvant contenir un chiffre sont alignées
sur une même ligne (ou colonne), le chiffre doit y aller — éliminez-le du
reste de cette ligne (ou colonne) en dehors de la boîte.</p>

<h3>7. Réduction Ligne/Boîte (Box/Line Reduction)</h3>
<p>Symétrique du pointant : si un chiffre d'une ligne (ou colonne) est confiné
à une seule boîte, éliminez-le du reste de cette boîte.</p>

<h3>8. X-Wing</h3>
<p>Si deux lignes limitent un chiffre aux deux mêmes colonnes, le chiffre forme
un rectangle 2×2. Il doit occuper deux coins opposés, donc on peut l'éliminer
de ces deux colonnes dans toutes les autres lignes. Le motif fonctionne aussi
avec lignes et colonnes inversées.</p>

<h3>Au-delà du X-Wing</h3>
<p>Les grilles les plus difficiles peuvent nécessiter Swordfish, XY-Wing,
coloration ou Nishio — ces techniques ne sont pas encore proposées en indice,
mais le solveur interne rapide les traite par backtracking, donc
<b>Résoudre</b> fonctionne toujours.</p>
"""


class _TextDialog(QDialog):
    def __init__(self, title: str, html: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720, 560)
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setHtml(html)
        browser.setOpenExternalLinks(True)
        f = QFont("Segoe UI", 10)
        browser.setFont(f)
        layout.addWidget(browser)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_label = "Fermer" if get_language() == "fr" else "Close"
        btn = QPushButton(close_label)
        btn.clicked.connect(self.accept)
        btn_row.addWidget(btn)
        layout.addLayout(btn_row)


def show_howto(parent=None) -> None:
    html = HOWTO_FR if get_language() == "fr" else HOWTO_EN
    _TextDialog(T("help_title"), html, parent).exec()


def show_techniques(parent=None) -> None:
    html = TECHNIQUES_FR if get_language() == "fr" else TECHNIQUES_EN
    _TextDialog(T("techniques_title"), html, parent).exec()

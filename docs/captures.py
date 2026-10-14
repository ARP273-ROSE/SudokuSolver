"""Captures RÉELLES de la fenêtre pour le manuel, dans les deux langues.

    QT_QPA_PLATFORM=offscreen python docs/captures.py      (depuis la racine)

Même fenêtre et même style figé que le programme livré ; une grille générée
avec une graine fixe, pour que les captures soient reproductibles.
"""
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
SORTIE = RACINE / "docs" / "captures"

from PyQt6.QtCore import QCoreApplication  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402


def attendre(app, condition, delai=30):
    fin = time.time() + delai
    while time.time() < fin and not condition():
        app.processEvents()
        time.sleep(0.02)


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    app.setOrganizationName("ARP273-ROSE-captures")   # ne touche pas aux vrais réglages
    import interface_kit
    import main as programme
    interface_kit.appliquer_style(app, programme.COULEURS, polices=RACINE / "polices",
                                  famille="Source Sans 3", taille=10)
    from gui.main_window import MainWindow
    from i18n import set_language
    from sudoku import Board, Solver
    grille = ("530070000600195000098000060800060003400803001"
              "700020006060000280000419005000080079")
    for langue in ("fr", "en"):
        w = MainWindow()
        # la grille de démarrage est générée en fond : on attend qu'elle arrive
        attendre(app, lambda: w.btn_new.isEnabled() and w.grid.board.to_string() != '0' * 81)
        time.sleep(0.3)
        app.processEvents()
        w._set_lang(langue)
        set_language(langue)
        w._retranslate()
        board = Board.from_string(grille)
        w.solution_board = Solver().solve(board).solutions[0]
        w.original_board = board.copy()
        board.recompute_candidates()
        w.grid.set_board(board)
        w.lbl_hint.clear()
        w.resize(640, 860)
        w.show()
        app.processEvents()
        w.grab().save(str(SORTIE / f"{langue}-principal.png"))
        w._on_hint()
        app.processEvents()
        w.grab().save(str(SORTIE / f"{langue}-indice.png"))
        w.close()
        QCoreApplication.processEvents()
    print(f"captures écrites dans {SORTIE}")


if __name__ == "__main__":
    main()

"""SudokuSolver entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import crash_handler

# Install the global crash handler as early as possible so even
# failures during import of downstream modules are captured.
crash_handler.install()

from PyQt6.QtGui import QIcon  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from gui.main_window import MainWindow  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SudokuSolver")
    app.setOrganizationName("Kevin")
    app.setQuitOnLastWindowClosed(True)

    icon_path = Path(__file__).resolve().parent / "logo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    # Vigie anti-gel : le minuteur bat depuis le fil graphique, un fil de fond
    # regarde l'heure. Si le battement s'arrete, la fenetre est figee, et la
    # pile du fil graphique dit ce qui la retenait. Sans cela un gel ne laisse
    # aucune trace : on tue l'application et on ne peut rien en dire.
    try:
        import reporting
        from PyQt6.QtCore import QTimer

        vigie = reporting.Vigie(seuil=10.0, periode=2.0)
        vigie.demarrer()
        minuteur = QTimer(window)
        minuteur.timeout.connect(vigie.battre)
        minuteur.start(2000)
        window._vigie = vigie          # garde une reference vivante
        window._vigie_timer = minuteur
    except Exception:
        pass

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

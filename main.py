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
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

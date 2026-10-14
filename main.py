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


#: palette claire de l'application (rôles complétés par interface_kit)
COULEURS = {
    "fenetre": "#eef2f8", "texte": "#1a2433", "base": "#ffffff",
    "base_alt": "#f4f7fc", "bouton": "#e3e9f3", "texte_bouton": "#1a2433",
    "selection": "#2e5a88", "texte_selection": "#ffffff", "lien": "#1c6db4",
    "infobulle": "#fffdf3", "texte_infobulle": "#1a2433", "desactive": "#8a94a6",
    "clair": "#ffffff", "moyen": "#b8c3d4", "sombre": "#7d8798",
}


def _verifier() -> int:
    """--check : l'application et ses dépendances se chargent-elles ?

    Lancé par la construction des paquets (Windows, macOS, Linux) avec
    l'interpréteur embarqué. Aucune fenêtre n'est ouverte.
    """
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        import i18n  # noqa: F401
        import reporting  # noqa: F401
        import updater  # noqa: F401
        import interface_kit  # noqa: F401
        from sudoku import Generator, Solver  # noqa: F401
        app = QApplication.instance() or QApplication(sys.argv[:1])
        del app
    except Exception as exc:
        print(f"SudokuSolver : ECHEC / FAILED -- {type(exc).__name__}: {exc}")
        return 1
    print("SudokuSolver : OK")
    return 0


def main() -> int:
    if "--check" in sys.argv[1:]:
        return _verifier()
    app = QApplication(sys.argv)
    app.setApplicationName("SudokuSolver")
    # Seul réglage QSettings : la langue choisie dans le menu Langue.
    app.setOrganizationName("ARP273-ROSE")
    app.setQuitOnLastWindowClosed(True)

    # Verrou nommé lu par l'installeur Inno (AppMutex = <nom_fichier>EnCours) :
    # installer par-dessus une application ouverte ne remplacerait pas les
    # fichiers en cours d'utilisation, et annoncerait pourtant « terminé ».
    if sys.platform == "win32":
        try:
            import ctypes
            app._mutex_installeur = ctypes.windll.kernel32.CreateMutexW(
                None, False, "SudokuSolverEnCours")
        except Exception:
            pass

    # Apparence FIGÉE : Fusion, palette complète et police embarquée, quel
    # que soit le thème (clair/sombre) ou les polices du système ; sous Linux,
    # vraies boîtes de fichiers complètes (interface_kit, kit commun).
    try:
        import interface_kit
        interface_kit.appliquer_style(
            app, COULEURS, polices=Path(__file__).resolve().parent / "polices",
            famille="Source Sans 3", taille=10)
        interface_kit.installer_dialogues_fichiers()
    except Exception:
        app.setStyle("Fusion")

    icon_path = Path(__file__).resolve().parent / "logo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    # Accord pour l'envoi automatique des rapports (premier lancement), puis
    # preuve de vie ; et recherche silencieuse des mises à jour 3 s après
    # l'ouverture, seulement pour une version installée.
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(1200, window.ask_report_consent)
    try:
        import updater
        if updater.is_packaged():
            QTimer.singleShot(3000, lambda: window._check_update(manual=False))
    except Exception:
        pass

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
        minuteur.start(1000)           # avant le premier controle (2 s)
        window._vigie = vigie          # garde une reference vivante
        window._vigie_timer = minuteur
    except Exception:
        pass

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

"""Global crash handler: captures unhandled exceptions, writes an
anonymized JSON report under ``crash_reports/``, and shows a message
to the user when a Qt application is alive.

Reports never contain the real username or home path — they are
replaced with ``~`` / ``<user>`` so the file can be sent to a bug
tracker without leaking identity.
"""

from __future__ import annotations

import json
import os
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
_fichier_faulthandler = None
CRASH_DIR = PROJECT_DIR / "crash_reports"
MAX_REPORTS = 50  # keep only the newest N reports


def _anonymize(text: str) -> str:
    """Redact the home path and username from a string."""
    try:
        home = str(Path.home())
        if home:
            text = text.replace(home, "~")
            text = text.replace(home.replace("\\", "/"), "~")
    except Exception:
        pass
    user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    if user and len(user) >= 3:
        text = text.replace(user, "<user>")
    return text


def _read_version() -> str:
    try:
        return (PROJECT_DIR / "VERSION").read_text(encoding="utf-8").strip()
    except Exception:
        return "unknown"


def _trim_old_reports() -> None:
    try:
        reports = sorted(CRASH_DIR.glob("*.json"))
        while len(reports) > MAX_REPORTS:
            reports[0].unlink(missing_ok=True)
            reports.pop(0)
    except Exception:
        pass


def _write_report(exc_type, exc_value, exc_tb) -> Path | None:
    try:
        CRASH_DIR.mkdir(exist_ok=True)
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        tb_str = _anonymize(tb_str)
        now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        data = {
            "timestamp": now,
            "app": "SudokuSolver",
            "version": _read_version(),
            "platform": _anonymize(platform.platform()),
            "python": platform.python_version(),
            "exception_type": exc_type.__name__ if exc_type else "",
            "exception_message": _anonymize(str(exc_value or "")),
            "traceback": tb_str,
        }
        path = CRASH_DIR / f"{now}.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        _trim_old_reports()
        return path
    except Exception:
        return None


def _show_dialog(exc_value, report_path: Path | None) -> None:
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox

        if QApplication.instance() is None:
            return
        msg = f"An unexpected error occurred:\n\n{type(exc_value).__name__}: {exc_value}"
        if report_path:
            msg += f"\n\nA crash report has been saved to:\n{report_path.name}"
        QMessageBox.critical(None, "SudokuSolver", msg)
    except Exception:
        pass


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    # Never swallow KeyboardInterrupt — let it propagate for Ctrl+C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    report = _write_report(exc_type, exc_value, exc_tb)
    # Le rapport part maintenant, tant que le processus vit encore ; s'il
    # n'aboutit pas il est mis en file et repartira au demarrage suivant.
    try:
        import traceback as _tb
        import reporting
        reporting.signaler_plantage(
            ''.join(_tb.format_exception(exc_type, exc_value, exc_tb)))
    except Exception:
        pass
    _show_dialog(exc_value, report)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def dossier_donnees() -> Path:
    """Ou vivent rapports et reglages.

    Dans le paquet installe, le dossier du programme peut etre en lecture
    seule selon l'endroit choisi : on prend donc %LOCALAPPDATA%. En
    developpement, on reste a cote du code, plus commode a inspecter.
    """
    if (PROJECT_DIR.parent / 'python' / 'python.exe').exists():
        base = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'SudokuSolver'
    else:
        base = PROJECT_DIR
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        base = Path.home()
    return base


def install() -> None:
    sys.excepthook = _excepthook

    # Remontee d'incidents. Une faute de segmentation dans Qt ne passe pas par
    # excepthook : l'application disparait sans un mot. faulthandler ecrit la
    # pile avant la mort, et on la releve au demarrage suivant.
    dossier = dossier_donnees()
    trace_native = dossier / '_crash_natif.log'
    try:
        import faulthandler
        global _fichier_faulthandler
        _fichier_faulthandler = open(trace_native, 'w', encoding='utf-8')
        faulthandler.enable(file=_fichier_faulthandler, all_threads=True)
    except Exception:
        pass
    try:
        import reporting
        version = ''
        for base in (PROJECT_DIR, PROJECT_DIR.parent):
            fichier = base / 'VERSION'
            if fichier.exists():
                version = fichier.read_text(encoding='utf-8').strip()
                break
        reporting.init(dossier, application='sudokusolver', version=version)
        reporting.relever_crash_natif(trace_native)
        reporting.reprendre_file_en_fond()
    except Exception:
        pass

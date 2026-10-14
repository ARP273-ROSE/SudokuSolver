# -*- coding: utf-8 -*-
"""Interface sous Xvfb : fenêtre dans les deux langues, langue mémorisée,
kit commun (mise à jour, rapports, accord) branché.

    xvfb-run -a python -m pytest -q tests/test_gui.py

Les réglages Qt et les données sont détournés vers un dossier temporaire
avant tout import de l'application.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix='sudoku-test-')
os.environ['HOME'] = _TMP
os.environ['XDG_CONFIG_HOME'] = os.path.join(_TMP, 'config')
os.environ.setdefault('QT_QPA_PLATFORM', 'xcb' if os.environ.get('DISPLAY') else 'offscreen')

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import pytest  # noqa: E402

pytest.importorskip('PyQt6')
from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

APP = QApplication.instance() or QApplication([])
APP.setOrganizationName('ARP273-ROSE')


def _menus(win):
    textes = []
    for action in win.menuBar().actions():
        textes.append(action.text())
        if action.menu():
            textes += [a.text() for a in action.menu().actions() if a.text()]
    return textes


def _fenetre():
    from gui.main_window import MainWindow
    win = MainWindow()
    win.show()
    APP.processEvents()
    return win


def test_langue_choisie_retenue_et_interface_traduite():
    import i18n
    win = _fenetre()
    win._set_lang('en')
    menus_en = _menus(win)
    assert '&Report a problem...' in menus_en
    for t in menus_en + [win.btn_new.text(), win.btn_hint.text(), win.windowTitle()]:
        assert not any(c in t for c in 'éèàçêôû'), t
    win._set_lang('fr')
    assert '&Signaler un problème...' in _menus(win)
    assert i18n.saved_language() == 'fr'
    win.close()
    # nouvelle fenêtre : le choix est retenu
    win2 = _fenetre()
    assert i18n.get_language() == 'fr'
    win2.close()


def test_mise_a_jour_passe_par_le_kit(monkeypatch):
    import updater
    vus, appels = [], []
    monkeypatch.setattr(updater, 'check', lambda v: appels.append(v) or None)
    monkeypatch.setattr(QMessageBox, 'information', lambda *a, **k: vus.append(a[2]))
    win = _fenetre()
    win._check_update(manual=True)
    win._upd_thread.join(5)
    for _ in range(20):
        APP.processEvents()
    assert appels == [win.version]
    assert vus, "aucun message « à jour »"
    win.close()


def test_accord_rapports_et_case_du_menu(monkeypatch):
    import reporting
    reporting.init(Path(_TMP) / 'donnees', application='sudoku-test', version='0')
    reporting.definir_consentement(False)
    monkeypatch.setattr(reporting, 'signaler_demarrage', lambda **k: None)
    win = _fenetre()
    win.ask_report_consent()                  # déjà répondu : aucune boîte
    win.act_autoreport.setChecked(True)
    assert reporting.consentement() is True
    win.act_autoreport.setChecked(False)
    assert reporting.consentement() is False
    win.close()


def test_check_en_ligne_de_commande():
    import subprocess
    r = subprocess.run([sys.executable, '-B', str(RACINE / 'main.py'), '--check'],
                       capture_output=True, text=True, timeout=120,
                       env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'})
    assert r.returncode == 0, r.stdout + r.stderr

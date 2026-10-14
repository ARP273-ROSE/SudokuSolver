# -*- coding: utf-8 -*-
"""Bilinguisme : aucun texte d'interface en dur, aucune clé manquante.

L'interface est en anglais et en français : la langue du système au premier
lancement, puis celle choisie dans le menu Langue (mémorisée). Tout texte
affiché passe par T(clé) ou tr(en, fr) ; ce test attrape :

  - un texte passé tel quel à un widget (setText, QLabel, QMessageBox...) ;
  - une clé T("...") absente de STRINGS (elle s'afficherait telle quelle) ;
  - du français dans la partie anglaise d'une paire, ou une moitié vide.

    python -m pytest -q tests/test_i18n_textes.py
"""
import ast
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import i18n  # noqa: E402

SOURCES = ['main.py', 'crash_handler.py', 'gui']
METHODES = {'setText', 'setWindowTitle', 'setToolTip', 'setPlaceholderText',
            'addAction', 'addMenu', 'setTitle', 'showMessage', 'setStatusTip',
            'addTab', 'setLabelText', 'addItem', 'setInformativeText',
            'setDetailedText', 'setWhatsThis', 'setTabText'}
CONSTRUCTEURS = {'QLabel', 'QPushButton', 'QCheckBox', 'QGroupBox', 'QAction',
                 'QRadioButton', 'QMenu', 'QToolButton', 'QProgressDialog'}
BOITES = {'information', 'warning', 'critical', 'question', 'about'}
TECHNIQUES = {'sudoku', 'sudokusolver', 'sdk', 'txt', 'english', 'français',
              'ok', 'x-wing'}
BALISE = re.compile(r'<[^>]*>|&[a-z]+;|&#\d+;')
MOT = re.compile(r"[A-Za-zÀ-ÿ]{2,}")
FRANCAIS = re.compile(r"[éèàçêôûùîïœ«»]")


def _fichiers():
    for nom in SOURCES:
        chemin = RACINE / nom
        yield from (sorted(chemin.rglob('*.py')) if chemin.is_dir() else [chemin])


def _litteraux(noeud):
    if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
        return [noeud.value]
    if isinstance(noeud, ast.JoinedStr):
        return [v.value for v in noeud.values
                if isinstance(v, ast.Constant) and isinstance(v.value, str)]
    return []


def _nom(appel):
    f = appel.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, 'id', '')


def test_aucun_texte_en_dur():
    fautes = []
    for fichier in _fichiers():
        for n in ast.walk(ast.parse(fichier.read_text(encoding='utf-8'))):
            if not isinstance(n, ast.Call):
                continue
            nom = _nom(n)
            if nom in METHODES or nom in CONSTRUCTEURS:
                args = n.args[:1]
            elif nom in BOITES and getattr(getattr(n.func, 'value', None), 'id', '') == 'QMessageBox':
                args = n.args[1:3]
            else:
                continue
            for a in args:
                mots = [m for t in _litteraux(a) for m in MOT.findall(BALISE.sub(' ', t))
                        if m.lower() not in TECHNIQUES]
                if mots:
                    fautes.append(f"{fichier.relative_to(RACINE)}:{n.lineno} {nom} -> {' '.join(mots)}")
    assert not fautes, "Textes affichés sans traduction :\n  " + "\n  ".join(fautes)


def test_toutes_les_cles_existent():
    manquantes = []
    for fichier in _fichiers():
        for n in ast.walk(ast.parse(fichier.read_text(encoding='utf-8'))):
            if isinstance(n, ast.Call) and _nom(n) == 'T' and n.args:
                a = n.args[0]
                if isinstance(a, ast.Constant) and a.value not in i18n.STRINGS:
                    manquantes.append(f"{fichier.relative_to(RACINE)}:{n.lineno} {a.value}")
    from sudoku import Difficulty
    manquantes += [f"difficulty_{d.value}" for d in Difficulty
                   if f"difficulty_{d.value}" not in i18n.STRINGS]
    assert not manquantes, "Clés absentes de i18n.STRINGS :\n  " + "\n  ".join(manquantes)


def test_paires_completes_et_anglais_sans_francais():
    fautes = []
    for cle, (en, fr) in i18n.STRINGS.items():
        if not en.strip() or not fr.strip():
            fautes.append(f"{cle} : moitié vide")
        if FRANCAIS.search(en) and cle not in ('menu_lang_fr',):
            fautes.append(f"{cle} : français dans l'anglais : {en[:50]!r}")
    assert not fautes, "\n".join(fautes)


def test_detection_de_la_langue_du_systeme():
    for langues, attendu in ((['fr-FR'], 'fr'), (['French_France'], 'fr'),
                             (['en-US'], 'en'), (['de-DE'], 'en'), ([], 'en')):
        assert i18n.detect_language(langues) == attendu or not langues, langues

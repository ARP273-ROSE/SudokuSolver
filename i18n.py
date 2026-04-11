"""Bilingual FR/EN translation layer.

All UI strings are defined as (en, fr) pairs. The active language is
detected from the system locale on first use (falls back to English).
Use `T(key)` to look up a translated string, or `tr(en, fr)` for inline
translations.
"""

from __future__ import annotations

import locale
import os
from typing import Dict, Tuple


_lang = "en"


def detect_language() -> str:
    """Detect FR/EN from system locale.

    Uses `locale.getlocale()` (the non-deprecated replacement for
    `getdefaultlocale()`), then falls back to environment variables,
    which works even when no locale has been set.
    """
    candidates: list[str] = []
    try:
        loc = locale.getlocale()
        if loc and loc[0]:
            candidates.append(loc[0])
    except Exception:
        pass
    for env in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        val = os.environ.get(env)
        if val:
            candidates.append(val)
    for c in candidates:
        if c and c.lower().startswith("fr"):
            return "fr"
    return "en"


def set_language(lang: str) -> None:
    global _lang
    if lang in ("en", "fr"):
        _lang = lang


def get_language() -> str:
    return _lang


def tr(en: str, fr: str) -> str:
    return fr if _lang == "fr" else en


# Keyed translations used across the GUI. Structure: key -> (en, fr)
STRINGS: Dict[str, Tuple[str, str]] = {
    # Window
    "app_title": ("SudokuSolver", "SudokuSolver"),
    "app_subtitle": (
        "Solve, generate and learn Sudoku",
        "Résolvez, générez et apprenez le Sudoku",
    ),
    # Menu
    "menu_file": ("&File", "&Fichier"),
    "menu_new": ("&New puzzle", "&Nouvelle grille"),
    "menu_open": ("&Open...", "&Ouvrir..."),
    "menu_save": ("&Save...", "&Enregistrer..."),
    "menu_quit": ("&Quit", "&Quitter"),
    "menu_solve": ("&Solve", "&Résoudre"),
    "menu_solve_full": ("Solve &completely", "Résoudre &entièrement"),
    "menu_solve_step": ("Solve &step by step", "Résoudre &pas à pas"),
    "menu_hint": ("&Hint", "&Indice"),
    "menu_check": ("&Check", "&Vérifier"),
    "menu_clear": ("C&lear", "&Effacer"),
    "menu_language": ("&Language", "&Langue"),
    "menu_lang_en": ("English", "Anglais"),
    "menu_lang_fr": ("French", "Français"),
    "menu_help": ("&Help", "&Aide"),
    "menu_help_show": ("&How to play", "&Comment jouer"),
    "menu_techniques": ("Solving &techniques", "&Techniques de résolution"),
    "menu_about": ("&About", "À &propos"),
    # Difficulty
    "difficulty": ("Difficulty", "Difficulté"),
    "difficulty_easy": ("Easy", "Facile"),
    "difficulty_medium": ("Medium", "Moyen"),
    "difficulty_hard": ("Hard", "Difficile"),
    "difficulty_expert": ("Expert", "Expert"),
    # Buttons
    "btn_new": ("New puzzle", "Nouvelle grille"),
    "btn_solve": ("Solve", "Résoudre"),
    "btn_hint": ("Hint", "Indice"),
    "btn_step": ("Next step", "Étape suivante"),
    "btn_check": ("Check", "Vérifier"),
    "btn_clear": ("Clear", "Effacer"),
    "btn_reset": ("Reset", "Réinitialiser"),
    "btn_pencil": ("Pencil marks", "Candidats"),
    # Tooltips
    "tip_new": (
        "Generate a new puzzle with the selected difficulty",
        "Générer une nouvelle grille avec la difficulté sélectionnée",
    ),
    "tip_solve": (
        "Solve the puzzle completely (instant)",
        "Résoudre la grille entièrement (instantané)",
    ),
    "tip_hint": (
        "Show the next logical step with explanation",
        "Afficher la prochaine étape logique avec explication",
    ),
    "tip_step": (
        "Apply the next logical step",
        "Appliquer la prochaine étape logique",
    ),
    "tip_check": (
        "Check current entries against the solution",
        "Vérifier les chiffres saisis par rapport à la solution",
    ),
    "tip_clear": (
        "Clear non-given cells",
        "Effacer les cases non imposées",
    ),
    "tip_reset": (
        "Restore the original puzzle",
        "Restaurer la grille d'origine",
    ),
    "tip_pencil": (
        "Toggle candidate (pencil mark) display",
        "Afficher ou masquer les candidats (petits chiffres)",
    ),
    "tip_difficulty": (
        "Choose difficulty for new puzzles",
        "Choisir la difficulté des nouvelles grilles",
    ),
    "tip_grid_cell": (
        "Click a cell then type 1-9 (or 0/Delete to clear)",
        "Cliquez une case puis tapez 1-9 (ou 0/Suppr pour effacer)",
    ),
    # Status
    "status_ready": ("Ready", "Prêt"),
    "status_generating": ("Generating puzzle...", "Génération de la grille..."),
    "status_solved": ("Puzzle solved!", "Grille résolue !"),
    "status_no_solution": ("No solution found", "Aucune solution trouvée"),
    "status_multiple": (
        "Warning: this puzzle has multiple solutions",
        "Attention : cette grille a plusieurs solutions",
    ),
    "status_invalid": (
        "Invalid: the grid contains conflicts",
        "Invalide : la grille contient des conflits",
    ),
    "status_no_step": (
        "No logical step found — puzzle requires harder techniques",
        "Aucune étape logique trouvée — la grille requiert des techniques plus avancées",
    ),
    "status_generated": (
        "Generated {diff} puzzle ({clues} clues, hardest: {tech})",
        "Grille {diff} générée ({clues} indices, max : {tech})",
    ),
    "status_check_ok": (
        "All entries are correct so far",
        "Toutes les saisies sont correctes pour l'instant",
    ),
    "status_check_wrong": (
        "{n} incorrect entry/entries highlighted",
        "{n} saisie(s) incorrecte(s) mise(s) en évidence",
    ),
    # Dialogs
    "hint_title": ("Hint", "Indice"),
    "about_title": ("About SudokuSolver", "À propos de SudokuSolver"),
    "about_body": (
        "SudokuSolver v{version}\n\n"
        "A bilingual sudoku solver, generator and tutor.\n"
        "Implements constraint propagation, human-style techniques,\n"
        "and a difficulty-rated puzzle generator.\n\n"
        "Techniques: naked/hidden singles, naked/hidden pairs,\n"
        "naked triples, pointing, box/line reduction, X-Wing.",
        "SudokuSolver v{version}\n\n"
        "Solveur, générateur et tuteur de sudoku bilingue.\n"
        "Propagation de contraintes, techniques humaines,\n"
        "générateur de grilles par difficulté.\n\n"
        "Techniques : singles nus/cachés, paires nues/cachées,\n"
        "triplets nus, pointants, réduction ligne/boîte, X-Wing.",
    ),
    "help_title": ("How to play", "Comment jouer"),
    "techniques_title": ("Solving techniques", "Techniques de résolution"),
}


def T(key: str, **kwargs) -> str:
    en, fr = STRINGS.get(key, (key, key))
    s = fr if _lang == "fr" else en
    if kwargs:
        try:
            return s.format(**kwargs)
        except (KeyError, IndexError):
            return s
    return s

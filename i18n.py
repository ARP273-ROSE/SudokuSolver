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


def detect_language(ui_languages=None) -> str:
    """Detect FR/EN from the system.

    Qt's display languages first (`QLocale.system().uiLanguages()`, correct
    on Windows, macOS and Linux), then `locale.getlocale()`, then the
    environment variables. On Windows the Python locale reads like
    "French_France": the comparison ignores case and accepts "french".
    """
    candidates: list[str] = list(ui_languages or [])
    if ui_languages is None:
        try:
            from PyQt6.QtCore import QLocale
            candidates += list(QLocale.system().uiLanguages())[:1]
        except Exception:
            pass
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
        if c:
            return "fr" if c.lower().startswith(("fr", "french")) else "en"
    return "en"


def _settings():
    from PyQt6.QtCore import QSettings
    return QSettings("ARP273-ROSE", "SudokuSolver")


def saved_language() -> str | None:
    """Language chosen in the Language menu, if any (kept between runs)."""
    try:
        value = _settings().value("lang")
    except Exception:
        return None
    return value if value in ("en", "fr") else None


def save_language(lang: str) -> None:
    try:
        if lang in ("en", "fr"):
            _settings().setValue("lang", lang)
    except Exception:
        pass


def startup_language() -> str:
    """The saved choice, otherwise the system's language."""
    return saved_language() or detect_language()


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
    "menu_update": ("Check for &updates...", "Rechercher des &mises à jour..."),
    "menu_report": ("&Report a problem...", "&Signaler un problème..."),
    "menu_autoreport": (
        "Send problem reports automatically",
        "Envoyer automatiquement les rapports de problème",
    ),
    # Updates
    "update_title": ("Updates", "Mises à jour"),
    "update_checking": ("Checking for updates...", "Recherche de mises à jour..."),
    "update_uptodate": (
        "You are up to date (version {current}).",
        "Vous êtes à jour (version {current}).",
    ),
    "update_available": (
        "Version {version} is available (installed: {current}).",
        "La version {version} est disponible (installée : {current}).",
    ),
    "update_install": ("Install and restart", "Installer et redémarrer"),
    "update_sources": (
        "This copy runs from the sources: download the new version from the release page.",
        "Cette copie tourne depuis les sources : téléchargez la nouvelle version sur la page de publication.",
    ),
    "update_open_page": ("Open the download page", "Ouvrir la page de téléchargement"),
    "update_later": ("Later", "Plus tard"),
    "update_downloading": ("Downloading the update...", "Téléchargement de la mise à jour..."),
    "update_locked": (
        "A file of the application is in use. Close every SudokuSolver window and try again.",
        "Un fichier de l'application est en cours d'utilisation. Fermez toutes les fenêtres de SudokuSolver et réessayez.",
    ),
    "update_failed": ("The update failed:\n{error}", "La mise à jour a échoué :\n{error}"),
    "update_restart": (
        "The update is installed. SudokuSolver will now restart.",
        "La mise à jour est installée. SudokuSolver va redémarrer.",
    ),
    # Problem reports
    "consent_title": (
        "Send problem reports automatically?",
        "Envoyer automatiquement les rapports de problème ?",
    ),
    "consent_text": (
        "When SudokuSolver crashes or freezes, a short technical report (version, "
        "system, error trace) can be sent so the problem gets fixed. Nothing else is "
        "sent. You can change this at any time in the Help menu.",
        "Quand SudokuSolver plante ou se fige, un court rapport technique (version, "
        "système, trace de l'erreur) peut être transmis pour que le problème soit "
        "corrigé. Rien d'autre n'est envoyé. Ce choix se modifie à tout moment dans "
        "le menu Aide.",
    ),
    "consent_yes": ("Yes, send them", "Oui, les envoyer"),
    "consent_no": ("No", "Non"),
    "report_title": ("Report a problem", "Signaler un problème"),
    "report_prompt": (
        "Describe what happened and what you were doing:",
        "Décrivez ce qui s'est passé et ce que vous faisiez :",
    ),
    "report_placeholder": (
        "For example: the hint button stopped responding after...",
        "Par exemple : le bouton Indice ne répondait plus après...",
    ),
    "report_note": (
        "The report contains the version, the system and the recent log.",
        "Le rapport contient la version, le système et le journal récent.",
    ),
    "report_send": ("Send", "Envoyer"),
    "report_cancel": ("Cancel", "Annuler"),
    "report_empty": (
        "Nothing was sent: the description is empty.",
        "Rien n'a été envoyé : la description est vide.",
    ),
    "report_sent": ("Your report has been sent. Thank you.", "Votre signalement a été transmis. Merci."),
    "report_local": (
        "No connection: the report was saved here:\n{path}",
        "Pas de connexion : le signalement est enregistré ici :\n{path}",
    ),
    # Errors
    "error": ("Error: {error}", "Erreur : {error}"),
    "file_too_large": (
        "File too large ({size} bytes). Maximum: {max} bytes.",
        "Fichier trop volumineux ({size} octets). Maximum : {max} octets.",
    ),
    "file_filter_open": ("Sudoku (*.sdk *.txt);;All files (*)", "Sudoku (*.sdk *.txt);;Tous les fichiers (*)"),
    "file_filter_save": ("Sudoku (*.sdk);;Text (*.txt)", "Sudoku (*.sdk);;Texte (*.txt)"),
    "crash_text": (
        "An unexpected error occurred:\n\n{error}",
        "Une erreur inattendue s'est produite :\n\n{error}",
    ),
    "crash_saved": (
        "A crash report has been saved to:\n{name}",
        "Un rapport de plantage a été enregistré :\n{name}",
    ),
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

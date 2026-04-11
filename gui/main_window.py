"""Main window for SudokuSolver."""

from __future__ import annotations

import inspect
import logging
import os
import traceback
from functools import wraps
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from i18n import T, detect_language, get_language, set_language
from sudoku import (
    Board,
    Difficulty,
    Generator,
    HumanSolver,
    Solver,
    Technique,
)
from sudoku.techniques import apply_step

from .grid_widget import GridWidget
from .help_dialog import show_howto, show_techniques


PROJECT_DIR = Path(__file__).resolve().parent.parent
MAX_PUZZLE_FILE_BYTES = 10 * 1024  # 10 KB — any sudoku file is <200 bytes
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "sudoku.log"

log = logging.getLogger("SudokuSolver")


def _setup_logging() -> None:
    try:
        import logging.handlers
        LOG_DIR.mkdir(exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=200_000, backupCount=2, encoding="utf-8"
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        log.addHandler(handler)
        log.setLevel(logging.INFO)
    except Exception:
        pass


_setup_logging()


def _guarded(fn: Callable) -> Callable:
    """Decorator for Qt slot handlers: catch and log exceptions, and
    silently drop any extra positional arguments the signal may have
    emitted (e.g. the ``bool`` that ``QPushButton.clicked`` and
    ``QAction.triggered`` send out). This lets a simple
    ``def _on_foo(self):`` slot be connected directly to any signal.
    """
    sig = inspect.signature(fn)
    has_var_positional = any(
        p.kind == inspect.Parameter.VAR_POSITIONAL
        for p in sig.parameters.values()
    )
    # Count positional params, excluding `self`
    n_pos = sum(
        1
        for p in sig.parameters.values()
        if p.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
        )
    ) - 1

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            if has_var_positional:
                return fn(self, *args, **kwargs)
            return fn(self, *args[:n_pos], **kwargs)
        except Exception as exc:
            log.exception("Error in %s", fn.__name__)
            try:
                self.status.showMessage(f"Error: {exc}")
                QMessageBox.warning(
                    self, T("app_title"), f"{type(exc).__name__}: {exc}"
                )
            except Exception:
                pass

    return wrapper


def _read_version() -> str:
    try:
        return (PROJECT_DIR / "VERSION").read_text(encoding="utf-8").strip()
    except Exception:
        return "1.0.0"


class GenerateWorker(QThread):
    done = pyqtSignal(object)       # GeneratedPuzzle
    failed = pyqtSignal(str)        # error message

    def __init__(self, difficulty: Difficulty):
        super().__init__()
        self.difficulty = difficulty

    def run(self) -> None:
        try:
            gen = Generator()
            gp = gen.generate(self.difficulty)
            self.done.emit(gp)
        except Exception as exc:
            log.exception("GenerateWorker failed")
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class SolveWorker(QThread):
    """Runs the fast solver in the background so even pathological user
    input can't freeze the UI. The caller receives a SolveResult or an
    error string."""

    done = pyqtSignal(object)       # SolveResult
    failed = pyqtSignal(str)

    def __init__(self, board: Board):
        super().__init__()
        # Defensive copy — the main thread may keep mutating the board.
        self.board = board.copy()

    def run(self) -> None:
        try:
            solver = Solver(max_solutions=2, max_nodes=2_000_000)
            result = solver.solve(self.board)
            self.done.emit(result)
        except Exception as exc:
            log.exception("SolveWorker failed")
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        set_language(detect_language())

        self.version = _read_version()
        self.original_board: Board = Board()
        self.solution_board: Board = Board()
        self.current_difficulty: Difficulty = Difficulty.EASY
        self.human_solver = HumanSolver()
        self.fast_solver = Solver(max_solutions=2, max_nodes=2_000_000)
        self.gen_worker: GenerateWorker | None = None
        self.solve_worker: SolveWorker | None = None

        self._build_ui()
        self._retranslate()

        icon_path = PROJECT_DIR / "logo.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Start with an easy puzzle
        self._generate(Difficulty.EASY)

    # ---- UI construction ----

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Top bar: difficulty + generate
        top = QHBoxLayout()
        self.lbl_difficulty = QLabel()
        self.cmb_difficulty = QComboBox()
        for d in Difficulty:
            self.cmb_difficulty.addItem(d.value, d)
        self.btn_new = QPushButton()
        self.btn_new.clicked.connect(self._on_new)
        top.addWidget(self.lbl_difficulty)
        top.addWidget(self.cmb_difficulty)
        top.addWidget(self.btn_new)
        top.addStretch()
        root.addLayout(top)

        # Grid
        self.grid = GridWidget()
        self.grid.cellChanged.connect(self._on_cell_changed)
        root.addWidget(self.grid, stretch=1)

        # Action buttons
        actions = QHBoxLayout()
        self.btn_hint = QPushButton()
        self.btn_hint.clicked.connect(self._on_hint)
        self.btn_step = QPushButton()
        self.btn_step.clicked.connect(self._on_next_step)
        self.btn_solve = QPushButton()
        self.btn_solve.clicked.connect(self._on_solve)
        self.btn_check = QPushButton()
        self.btn_check.clicked.connect(self._on_check)
        self.btn_pencil = QPushButton()
        self.btn_pencil.setCheckable(True)
        self.btn_pencil.setChecked(True)
        self.btn_pencil.clicked.connect(self._on_toggle_candidates)
        self.btn_reset = QPushButton()
        self.btn_reset.clicked.connect(self._on_reset)
        for b in (
            self.btn_hint,
            self.btn_step,
            self.btn_solve,
            self.btn_check,
            self.btn_pencil,
            self.btn_reset,
        ):
            actions.addWidget(b)
        root.addLayout(actions)

        # Explanation label
        self.lbl_hint = QLabel()
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setStyleSheet(
            "QLabel { background: #f6f9ff; border: 1px solid #c9d4e8;"
            " border-radius: 6px; padding: 8px; color: #1a3a5c; }"
        )
        self.lbl_hint.setMinimumHeight(60)
        root.addWidget(self.lbl_hint)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Menus
        self._build_menus()

        self.setMinimumSize(620, 820)

    def _build_menus(self) -> None:
        mb = self.menuBar()

        self.menu_file = mb.addMenu("")
        self.act_new = QAction(self)
        self.act_new.triggered.connect(self._on_new)
        self.menu_file.addAction(self.act_new)
        self.act_open = QAction(self)
        self.act_open.triggered.connect(self._on_open)
        self.menu_file.addAction(self.act_open)
        self.act_save = QAction(self)
        self.act_save.triggered.connect(self._on_save)
        self.menu_file.addAction(self.act_save)
        self.menu_file.addSeparator()
        self.act_quit = QAction(self)
        self.act_quit.triggered.connect(self.close)
        self.menu_file.addAction(self.act_quit)

        self.menu_solve = mb.addMenu("")
        self.act_solve_full = QAction(self)
        self.act_solve_full.triggered.connect(self._on_solve)
        self.menu_solve.addAction(self.act_solve_full)
        self.act_solve_step = QAction(self)
        self.act_solve_step.triggered.connect(self._on_next_step)
        self.menu_solve.addAction(self.act_solve_step)
        self.act_hint = QAction(self)
        self.act_hint.triggered.connect(self._on_hint)
        self.menu_solve.addAction(self.act_hint)
        self.act_check = QAction(self)
        self.act_check.triggered.connect(self._on_check)
        self.menu_solve.addAction(self.act_check)
        self.act_clear = QAction(self)
        self.act_clear.triggered.connect(self._on_reset)
        self.menu_solve.addAction(self.act_clear)

        self.menu_lang = mb.addMenu("")
        self.act_lang_en = QAction(self, checkable=True)
        self.act_lang_fr = QAction(self, checkable=True)
        lang_group = QActionGroup(self)
        lang_group.addAction(self.act_lang_en)
        lang_group.addAction(self.act_lang_fr)
        self.act_lang_en.triggered.connect(lambda: self._set_lang("en"))
        self.act_lang_fr.triggered.connect(lambda: self._set_lang("fr"))
        if get_language() == "fr":
            self.act_lang_fr.setChecked(True)
        else:
            self.act_lang_en.setChecked(True)
        self.menu_lang.addAction(self.act_lang_en)
        self.menu_lang.addAction(self.act_lang_fr)

        self.menu_help = mb.addMenu("")
        self.act_help_show = QAction(self)
        self.act_help_show.triggered.connect(lambda: show_howto(self))
        self.menu_help.addAction(self.act_help_show)
        self.act_techniques = QAction(self)
        self.act_techniques.triggered.connect(lambda: show_techniques(self))
        self.menu_help.addAction(self.act_techniques)
        self.menu_help.addSeparator()
        self.act_about = QAction(self)
        self.act_about.triggered.connect(self._on_about)
        self.menu_help.addAction(self.act_about)

    # ---- Retranslate everything ----

    def _retranslate(self) -> None:
        self.setWindowTitle(f"{T('app_title')} v{self.version} — {T('app_subtitle')}")

        self.lbl_difficulty.setText(T("difficulty") + " :")
        # Refresh difficulty labels
        self.cmb_difficulty.blockSignals(True)
        current = self.cmb_difficulty.currentData()
        self.cmb_difficulty.clear()
        for d in Difficulty:
            self.cmb_difficulty.addItem(T(f"difficulty_{d.value}"), d)
        idx = list(Difficulty).index(current or Difficulty.EASY)
        self.cmb_difficulty.setCurrentIndex(idx)
        self.cmb_difficulty.blockSignals(False)
        self.cmb_difficulty.setToolTip(T("tip_difficulty"))

        self.btn_new.setText(T("btn_new"))
        self.btn_new.setToolTip(T("tip_new"))
        self.btn_hint.setText(T("btn_hint"))
        self.btn_hint.setToolTip(T("tip_hint"))
        self.btn_step.setText(T("btn_step"))
        self.btn_step.setToolTip(T("tip_step"))
        self.btn_solve.setText(T("btn_solve"))
        self.btn_solve.setToolTip(T("tip_solve"))
        self.btn_check.setText(T("btn_check"))
        self.btn_check.setToolTip(T("tip_check"))
        self.btn_pencil.setText(T("btn_pencil"))
        self.btn_pencil.setToolTip(T("tip_pencil"))
        self.btn_reset.setText(T("btn_reset"))
        self.btn_reset.setToolTip(T("tip_reset"))

        self.grid.setToolTip(T("tip_grid_cell"))

        self.menu_file.setTitle(T("menu_file"))
        self.act_new.setText(T("menu_new"))
        self.act_open.setText(T("menu_open"))
        self.act_save.setText(T("menu_save"))
        self.act_quit.setText(T("menu_quit"))

        self.menu_solve.setTitle(T("menu_solve"))
        self.act_solve_full.setText(T("menu_solve_full"))
        self.act_solve_step.setText(T("menu_solve_step"))
        self.act_hint.setText(T("menu_hint"))
        self.act_check.setText(T("menu_check"))
        self.act_clear.setText(T("menu_clear"))

        self.menu_lang.setTitle(T("menu_language"))
        self.act_lang_en.setText(T("menu_lang_en"))
        self.act_lang_fr.setText(T("menu_lang_fr"))

        self.menu_help.setTitle(T("menu_help"))
        self.act_help_show.setText(T("menu_help_show"))
        self.act_techniques.setText(T("menu_techniques"))
        self.act_about.setText(T("menu_about"))

        self.status.showMessage(T("status_ready"))

    def _set_lang(self, lang: str) -> None:
        set_language(lang)
        self._retranslate()

    # ---- Actions ----

    @_guarded
    def _on_new(self) -> None:
        diff = self.cmb_difficulty.currentData()
        if diff is None:
            diff = Difficulty.EASY
        self._generate(diff)

    def _generate(self, difficulty: Difficulty) -> None:
        # Refuse to start a second generation while one is running.
        if self._worker_is_running(self.gen_worker):
            return
        self.current_difficulty = difficulty
        self.status.showMessage(T("status_generating"))
        self.btn_new.setEnabled(False)
        self._dispose_gen_worker()
        worker = GenerateWorker(difficulty)
        worker.done.connect(self._on_generated)
        worker.failed.connect(self._on_worker_failed)
        worker.finished.connect(self._on_gen_worker_finished)
        self.gen_worker = worker
        worker.start()

    @staticmethod
    def _worker_is_running(w) -> bool:
        """Safely test if a QThread is still alive. Returns False if the
        Python wrapper is attached to a deleted C++ object."""
        if w is None:
            return False
        try:
            return bool(w.isRunning())
        except RuntimeError:
            return False

    def _on_gen_worker_finished(self) -> None:
        w = self.gen_worker
        self.gen_worker = None
        if w is not None:
            try:
                w.deleteLater()
            except RuntimeError:
                pass

    def _dispose_gen_worker(self) -> None:
        w = self.gen_worker
        self.gen_worker = None
        if w is None:
            return
        try:
            if w.isRunning():
                w.wait(5000)
        except RuntimeError:
            pass

    def _on_generated(self, gp) -> None:
        try:
            self.original_board = gp.puzzle.copy()
            self.solution_board = gp.solution.copy()
            board = gp.puzzle.copy()
            board.recompute_candidates()
            self.grid.set_board(board)
            self.lbl_hint.clear()
            tech_name = (
                gp.hardest_technique.value.replace("_", " ")
                if gp.hardest_technique
                else "—"
            )
            self.status.showMessage(
                T(
                    "status_generated",
                    diff=T(f"difficulty_{gp.difficulty.value}"),
                    clues=gp.clue_count,
                    tech=tech_name,
                )
            )
        finally:
            self.btn_new.setEnabled(True)

    def _on_worker_failed(self, message: str) -> None:
        log.error("Worker failed: %s", message)
        self.status.showMessage(f"Error: {message}")
        self.btn_new.setEnabled(True)
        self.btn_solve.setEnabled(True)

    @_guarded
    def _on_cell_changed(self, idx: int, value: int) -> None:
        self.grid.clear_hint()
        self.lbl_hint.clear()
        conflicts = self.grid.board.conflicts()
        # Inline conflict highlighting — user sees mistakes as they type.
        self.grid.set_errors(conflicts)
        if conflicts:
            self.status.showMessage(T("status_invalid"))
        elif self.grid.board.is_complete():
            self.status.showMessage(T("status_solved"))
        else:
            self.status.showMessage(T("status_ready"))

    @_guarded
    def _on_solve(self) -> None:
        # Reject conflicting user input before spawning work.
        if self.grid.board.conflicts():
            QMessageBox.warning(self, T("app_title"), T("status_invalid"))
            return
        if self._worker_is_running(self.solve_worker):
            return
        self.status.showMessage(T("status_generating"))  # "solving..." feel
        self.btn_solve.setEnabled(False)
        self._dispose_solve_worker()
        worker = SolveWorker(self.grid.board)
        worker.done.connect(self._on_solve_done)
        worker.failed.connect(self._on_worker_failed)
        worker.finished.connect(self._on_solve_worker_finished)
        self.solve_worker = worker
        worker.start()

    def _on_solve_worker_finished(self) -> None:
        w = self.solve_worker
        self.solve_worker = None
        if w is not None:
            try:
                w.deleteLater()
            except RuntimeError:
                pass

    def _dispose_solve_worker(self) -> None:
        w = self.solve_worker
        self.solve_worker = None
        if w is None:
            return
        try:
            if w.isRunning():
                w.wait(5000)
        except RuntimeError:
            pass

    def _on_solve_done(self, result) -> None:
        try:
            if result.timed_out and not result.solved:
                self.status.showMessage(T("status_no_solution"))
                return
            if not result.solved:
                self.status.showMessage(T("status_no_solution"))
                return
            if len(result.solutions) > 1:
                QMessageBox.warning(self, T("app_title"), T("status_multiple"))
            sol = result.solutions[0]
            b = self.grid.board
            for i in range(81):
                b.cells[i] = sol.cells[i]
            b.recompute_candidates()
            self.grid.set_board(b)
            self.status.showMessage(T("status_solved"))
        finally:
            self.btn_solve.setEnabled(True)

    @_guarded
    def _on_hint(self) -> None:
        step = self.human_solver.next_step(self.grid.board)
        if step is None:
            self.lbl_hint.setText(T("status_no_step"))
            self.grid.clear_hint()
            return
        text = step.explanation_fr if get_language() == "fr" else step.explanation_en
        self.lbl_hint.setText(text)
        self.grid.set_hint_overlay(
            focus=step.focus_cells,
            affected=step.affected_cells,
            placement=step.placement,
        )

    @_guarded
    def _on_next_step(self) -> None:
        step = self.human_solver.next_step(self.grid.board)
        if step is None:
            self.lbl_hint.setText(T("status_no_step"))
            self.grid.clear_hint()
            return
        apply_step(self.grid.board, step)
        self.grid.set_board(self.grid.board)
        text = step.explanation_fr if get_language() == "fr" else step.explanation_en
        self.lbl_hint.setText(text)
        if self.grid.board.is_complete():
            self.status.showMessage(T("status_solved"))

    @_guarded
    def _on_check(self) -> None:
        if not self.solution_board.cells or all(v == 0 for v in self.solution_board.cells):
            return
        errors = set(self.grid.board.conflicts())
        for i in range(81):
            v = self.grid.board.cells[i]
            if v and v != self.solution_board.cells[i]:
                errors.add(i)
        self.grid.set_errors(errors)
        if errors:
            self.status.showMessage(T("status_check_wrong", n=len(errors)))
        else:
            self.status.showMessage(T("status_check_ok"))

    @_guarded
    def _on_toggle_candidates(self) -> None:
        self.grid.show_candidates = self.btn_pencil.isChecked()
        self.grid.update()

    @_guarded
    def _on_reset(self) -> None:
        b = self.original_board.copy()
        b.recompute_candidates()
        self.grid.set_board(b)
        self.lbl_hint.clear()
        self.status.showMessage(T("status_ready"))

    @_guarded
    def _on_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            T("menu_open"),
            str(PROJECT_DIR),
            "Sudoku (*.sdk *.txt);;All files (*.*)",
        )
        if not path:
            return
        p = Path(path).resolve()
        # Size cap — prevents OOM on huge or hostile files.
        try:
            size = p.stat().st_size
        except OSError as e:
            QMessageBox.critical(self, T("app_title"), str(e))
            return
        if size > MAX_PUZZLE_FILE_BYTES:
            QMessageBox.critical(
                self,
                T("app_title"),
                f"File too large ({size} bytes). Max: {MAX_PUZZLE_FILE_BYTES}.",
            )
            return
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            board = Board.from_string(text)
            result = self.fast_solver.solve(board)
            if result.solved:
                self.solution_board = result.solutions[0]
            else:
                self.solution_board = Board()
            self.original_board = board.copy()
            board.recompute_candidates()
            self.grid.set_board(board)
            self.status.showMessage(T("status_ready"))
        except ValueError as e:
            QMessageBox.critical(self, T("app_title"), str(e))
        except Exception as e:
            log.exception("Open failed")
            QMessageBox.critical(self, T("app_title"), f"{type(e).__name__}: {e}")

    @_guarded
    def _on_save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            T("menu_save"),
            str(PROJECT_DIR / "puzzle.sdk"),
            "Sudoku (*.sdk);;Text (*.txt)",
        )
        if not path:
            return
        p = Path(path).resolve()
        try:
            p.write_text(self.grid.board.to_string("."), encoding="utf-8")
            self.status.showMessage(T("status_ready"))
        except OSError as e:
            QMessageBox.critical(self, T("app_title"), str(e))

    @_guarded
    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            T("about_title"),
            T("about_body", version=self.version),
        )

    # ---- Lifecycle ----

    def closeEvent(self, event) -> None:
        """Ensure background threads are joined before the window dies."""
        self._dispose_gen_worker()
        self._dispose_solve_worker()
        super().closeEvent(event)

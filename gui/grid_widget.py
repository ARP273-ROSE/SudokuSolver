"""Interactive 9x9 sudoku grid widget for PyQt6.

Features:
  - Click to select, type 1-9 to fill, 0/Delete/Backspace to clear
  - Arrow keys to navigate
  - Visual distinction between givens (bold) and user entries (blue)
  - Highlights for selected cell, same-row/col/box peers, same-value cells
  - Pencil-mark (candidate) display toggle
  - Highlight lists driven by the hint system (focus/affected/eliminations)
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPen,
)
from PyQt6.QtWidgets import QWidget

from sudoku.board import Board


# Color palette
COLOR_BG = QColor("#fafbfc")
COLOR_GIVEN = QColor("#1a1a1a")
COLOR_USER = QColor("#1f4d80")
COLOR_ERROR = QColor("#c0392b")
COLOR_GRID = QColor("#2c3e50")
COLOR_GRID_THIN = QColor("#95a5a6")
COLOR_SELECTED = QColor("#b8d8ff")
COLOR_PEER = QColor("#e8f0fa")
COLOR_SAME = QColor("#ffeaa7")
COLOR_FOCUS = QColor("#a3e4b5")
COLOR_AFFECTED = QColor("#ffcccc")
COLOR_CANDIDATE = QColor("#7f8c8d")
COLOR_HINT_DIGIT = QColor("#27ae60")


class GridWidget(QWidget):
    cellChanged = pyqtSignal(int, int)  # idx, new_value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board: Board = Board()
        self.selected: int = 0
        self.show_candidates: bool = True
        self.errors: set[int] = set()
        # Hint overlays
        self.focus_cells: list[int] = []
        self.affected_cells: list[int] = []
        self.hint_digit: Optional[tuple[int, int]] = None  # (idx, digit)

        self.setMinimumSize(450, 450)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # ---- Public API ----

    def set_board(self, board: Board) -> None:
        self.board = board
        self.errors.clear()
        self.clear_hint()
        self.update()

    def clear_hint(self) -> None:
        self.focus_cells = []
        self.affected_cells = []
        self.hint_digit = None
        self.update()

    def set_hint_overlay(
        self,
        focus: list[int],
        affected: list[int],
        placement: Optional[tuple[int, int]] = None,
    ) -> None:
        self.focus_cells = focus or []
        self.affected_cells = affected or []
        self.hint_digit = placement
        self.update()

    def set_errors(self, errors: set[int]) -> None:
        self.errors = set(errors)
        self.update()

    def toggle_candidates(self) -> None:
        self.show_candidates = not self.show_candidates
        self.update()

    # ---- Input handling ----

    def mousePressEvent(self, event: QMouseEvent) -> None:
        cell = self._cell_at(event.position().x(), event.position().y())
        if cell is not None:
            self.selected = cell
            self.update()
        self.setFocus()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key.Key_Left:
            self._move(-1, 0)
        elif key == Qt.Key.Key_Right:
            self._move(1, 0)
        elif key == Qt.Key.Key_Up:
            self._move(0, -1)
        elif key == Qt.Key.Key_Down:
            self._move(0, 1)
        elif Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            d = key - Qt.Key.Key_0
            self._set_cell(self.selected, d)
        elif key in (Qt.Key.Key_0, Qt.Key.Key_Delete, Qt.Key.Key_Backspace, Qt.Key.Key_Space):
            self._set_cell(self.selected, 0)
        else:
            super().keyPressEvent(event)

    def _move(self, dx: int, dy: int) -> None:
        r, c = divmod(self.selected, 9)
        r = max(0, min(8, r + dy))
        c = max(0, min(8, c + dx))
        self.selected = r * 9 + c
        self.update()

    def _set_cell(self, idx: int, value: int) -> None:
        if idx in self.board.givens:
            return
        if value == 0:
            self.board.cells[idx] = 0
        else:
            self.board.cells[idx] = value
        self.board.recompute_candidates()
        self.errors.discard(idx)
        self.cellChanged.emit(idx, value)
        self.update()

    def _cell_at(self, x: float, y: float) -> Optional[int]:
        side = min(self.width(), self.height())
        if x < 0 or y < 0 or x >= side or y >= side:
            return None
        cs = side / 9
        c = int(x / cs)
        r = int(y / cs)
        if 0 <= r < 9 and 0 <= c < 9:
            return r * 9 + c
        return None

    # ---- Painting ----

    def paintEvent(self, event) -> None:
        side = min(self.width(), self.height())
        cs = side / 9
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(0, 0, side, side, COLOR_BG)

        sel_r, sel_c = divmod(self.selected, 9)
        sel_val = self.board.cells[self.selected]
        sel_box = (sel_r // 3, sel_c // 3)

        # Cell backgrounds
        for r in range(9):
            for c in range(9):
                idx = r * 9 + c
                rect = QRectF(c * cs, r * cs, cs, cs)
                if idx in self.affected_cells:
                    p.fillRect(rect, COLOR_AFFECTED)
                elif idx in self.focus_cells:
                    p.fillRect(rect, COLOR_FOCUS)
                elif idx == self.selected:
                    p.fillRect(rect, COLOR_SELECTED)
                elif (
                    r == sel_r
                    or c == sel_c
                    or (r // 3, c // 3) == sel_box
                ):
                    p.fillRect(rect, COLOR_PEER)
                if sel_val and self.board.cells[idx] == sel_val and idx != self.selected:
                    p.fillRect(rect, COLOR_SAME)

        # Digits
        big_font = QFont("Segoe UI", max(10, int(cs * 0.45)))
        big_font.setBold(True)
        small_font = QFont("Segoe UI", max(6, int(cs * 0.18)))

        for r in range(9):
            for c in range(9):
                idx = r * 9 + c
                v = self.board.cells[idx]
                rect = QRectF(c * cs, r * cs, cs, cs)
                if v:
                    if idx in self.errors:
                        p.setPen(COLOR_ERROR)
                    elif idx in self.board.givens:
                        p.setPen(COLOR_GIVEN)
                    else:
                        p.setPen(COLOR_USER)
                    p.setFont(big_font)
                    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(v))
                elif self.show_candidates:
                    mask = self.board.candidates[idx]
                    if mask:
                        p.setPen(COLOR_CANDIDATE)
                        p.setFont(small_font)
                        for d in range(1, 10):
                            if mask & (1 << (d - 1)):
                                sr = (d - 1) // 3
                                sc = (d - 1) % 3
                                sx = c * cs + (sc + 0.5) * cs / 3
                                sy = r * cs + (sr + 0.5) * cs / 3
                                sub = QRectF(sx - cs / 6, sy - cs / 6, cs / 3, cs / 3)
                                p.drawText(sub, Qt.AlignmentFlag.AlignCenter, str(d))

                if self.hint_digit and self.hint_digit[0] == idx:
                    p.setPen(COLOR_HINT_DIGIT)
                    p.setFont(big_font)
                    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(self.hint_digit[1]))

        # Grid lines
        thin = QPen(COLOR_GRID_THIN, 1)
        thick = QPen(COLOR_GRID, 3)
        for i in range(10):
            pen = thick if i % 3 == 0 else thin
            p.setPen(pen)
            x = i * cs
            p.drawLine(int(x), 0, int(x), int(side))
            p.drawLine(0, int(x), int(side), int(x))

        p.end()

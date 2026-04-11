"""Human-style sudoku solving techniques.

Each technique scans the board for a pattern and returns a `Step` describing
what was found: which cells are involved, which candidates to eliminate, or
which digit to place, plus a short bilingual explanation.

Implemented techniques (ordered by difficulty):
  1. Naked Single           - one candidate in a cell
  2. Hidden Single          - one cell in a unit for a digit
  3. Naked Pair             - two cells sharing the same two candidates
  4. Naked Triple           - three cells whose candidates ⊆ 3 digits
  5. Hidden Pair            - two digits confined to two cells of a unit
  6. Pointing Pair/Triple   - box candidates aligned on a row/col
  7. Box/Line Reduction     - row/col candidates confined to a single box
  8. X-Wing                 - 2x2 rectangle on rows or columns

References:
  - Peter Norvig, "Solving Every Sudoku Puzzle"
  - sudopedia.org, sudokuwiki.org (technique catalogue)
  - Knuth, "Dancing Links" (underlying exact-cover theory)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import Callable, Optional

from .board import (
    ALL_MASK,
    ALL_UNITS,
    BOXES,
    Board,
    COLS,
    PEERS,
    ROWS,
    UNITS_OF,
    bits_to_digits,
    popcount,
)


class Technique(Enum):
    NAKED_SINGLE = "naked_single"
    HIDDEN_SINGLE = "hidden_single"
    NAKED_PAIR = "naked_pair"
    NAKED_TRIPLE = "naked_triple"
    HIDDEN_PAIR = "hidden_pair"
    POINTING = "pointing"
    BOX_LINE = "box_line"
    X_WING = "x_wing"


TECHNIQUE_DIFFICULTY = {
    Technique.NAKED_SINGLE: 1,
    Technique.HIDDEN_SINGLE: 2,
    Technique.NAKED_PAIR: 3,
    Technique.NAKED_TRIPLE: 4,
    Technique.HIDDEN_PAIR: 4,
    Technique.POINTING: 5,
    Technique.BOX_LINE: 5,
    Technique.X_WING: 7,
}


@dataclass
class Step:
    """A single move or elimination produced by a technique."""

    technique: Technique
    # Cells directly involved in the pattern (for highlighting)
    focus_cells: list[int] = field(default_factory=list)
    # Cells whose candidates are eliminated by this step
    affected_cells: list[int] = field(default_factory=list)
    # Placement: if set, (cell_idx, digit) to place
    placement: Optional[tuple[int, int]] = None
    # Eliminations: list of (cell_idx, digit)
    eliminations: list[tuple[int, int]] = field(default_factory=list)
    # Digits relevant to the pattern (e.g., the pair values)
    digits: list[int] = field(default_factory=list)
    # Bilingual explanation: (en, fr)
    explanation_en: str = ""
    explanation_fr: str = ""


# ---------------------------------------------------------------------------
# Individual technique finders
# ---------------------------------------------------------------------------


def find_naked_single(board: Board) -> Optional[Step]:
    for i in range(81):
        if board.cells[i] == 0 and popcount(board.candidates[i]) == 1:
            d = board.candidates[i].bit_length()
            r, c = divmod(i, 9)
            return Step(
                technique=Technique.NAKED_SINGLE,
                focus_cells=[i],
                placement=(i, d),
                digits=[d],
                explanation_en=(
                    f"Cell R{r+1}C{c+1} has only one possible digit: {d}."
                ),
                explanation_fr=(
                    f"La case L{r+1}C{c+1} n'a qu'un seul chiffre possible : {d}."
                ),
            )
    return None


def _unit_name(unit: list[int]) -> tuple[str, str]:
    """Return (en, fr) label for a unit."""
    if unit in ROWS:
        r = unit[0] // 9
        return f"row {r+1}", f"ligne {r+1}"
    if unit in COLS:
        c = unit[0] % 9
        return f"column {c+1}", f"colonne {c+1}"
    if unit in BOXES:
        r = unit[0] // 9
        c = unit[0] % 9
        b = (r // 3) * 3 + (c // 3)
        return f"box {b+1}", f"boîte {b+1}"
    return "unit", "unité"


def find_hidden_single(board: Board) -> Optional[Step]:
    for unit in ALL_UNITS:
        for d in range(1, 10):
            bm = 1 << (d - 1)
            spot = -1
            already = False
            for idx in unit:
                if board.cells[idx] == d:
                    already = True
                    break
                if board.cells[idx] == 0 and (board.candidates[idx] & bm):
                    if spot == -1:
                        spot = idx
                    else:
                        spot = -2
                        break
            if already or spot < 0:
                continue
            name_en, name_fr = _unit_name(unit)
            r, c = divmod(spot, 9)
            return Step(
                technique=Technique.HIDDEN_SINGLE,
                focus_cells=[spot],
                placement=(spot, d),
                digits=[d],
                explanation_en=(
                    f"In {name_en}, digit {d} can only go in R{r+1}C{c+1}."
                ),
                explanation_fr=(
                    f"Dans la {name_fr}, le chiffre {d} ne peut aller qu'en L{r+1}C{c+1}."
                ),
            )
    return None


def find_naked_pair(board: Board) -> Optional[Step]:
    return _naked_subset(board, size=2, technique=Technique.NAKED_PAIR)


def find_naked_triple(board: Board) -> Optional[Step]:
    return _naked_subset(board, size=3, technique=Technique.NAKED_TRIPLE)


def _naked_subset(board: Board, size: int, technique: Technique) -> Optional[Step]:
    for unit in ALL_UNITS:
        empties = [i for i in unit if board.cells[i] == 0]
        if len(empties) <= size:
            continue
        for combo in combinations(empties, size):
            union = 0
            valid = True
            for i in combo:
                m = board.candidates[i]
                if popcount(m) < 2 or popcount(m) > size:
                    valid = False
                    break
                union |= m
            if not valid or popcount(union) != size:
                continue
            # Eliminate `union` from other cells of the unit
            elims = []
            for i in empties:
                if i in combo:
                    continue
                overlap = board.candidates[i] & union
                if overlap:
                    for d in bits_to_digits(overlap):
                        elims.append((i, d))
            if not elims:
                continue
            digits = bits_to_digits(union)
            name_en, name_fr = _unit_name(unit)
            label = "pair" if size == 2 else "triple"
            label_fr = "paire" if size == 2 else "triplet"
            return Step(
                technique=technique,
                focus_cells=list(combo),
                affected_cells=sorted({c for c, _ in elims}),
                eliminations=elims,
                digits=digits,
                explanation_en=(
                    f"Naked {label} {digits} in {name_en}: "
                    f"these digits must occupy the {size} focused cells, "
                    f"so they cannot appear elsewhere in the unit."
                ),
                explanation_fr=(
                    f"{label_fr.capitalize()} nue {digits} dans la {name_fr} : "
                    f"ces chiffres occupent forcément les {size} cases marquées, "
                    f"donc ils sont éliminés ailleurs dans l'unité."
                ),
            )
    return None


def find_hidden_pair(board: Board) -> Optional[Step]:
    for unit in ALL_UNITS:
        # For each pair of digits, find cells of the unit where either can go
        positions = {d: [] for d in range(1, 10)}
        for idx in unit:
            if board.cells[idx]:
                continue
            for d in bits_to_digits(board.candidates[idx]):
                positions[d].append(idx)
        for d1, d2 in combinations(range(1, 10), 2):
            p1, p2 = positions[d1], positions[d2]
            if len(p1) != 2 or len(p2) != 2 or set(p1) != set(p2):
                continue
            cells = p1
            mask = (1 << (d1 - 1)) | (1 << (d2 - 1))
            elims = []
            for idx in cells:
                extra = board.candidates[idx] & ~mask
                if extra:
                    for d in bits_to_digits(extra):
                        elims.append((idx, d))
            if not elims:
                continue
            name_en, name_fr = _unit_name(unit)
            return Step(
                technique=Technique.HIDDEN_PAIR,
                focus_cells=cells,
                affected_cells=cells,
                eliminations=elims,
                digits=[d1, d2],
                explanation_en=(
                    f"Hidden pair {{{d1},{d2}}} in {name_en}: these two digits "
                    f"can only appear in the two focused cells, so every other "
                    f"candidate in those cells is eliminated."
                ),
                explanation_fr=(
                    f"Paire cachée {{{d1},{d2}}} dans la {name_fr} : ces deux "
                    f"chiffres ne peuvent apparaître que dans les deux cases "
                    f"marquées, donc tous les autres candidats de ces cases sont éliminés."
                ),
            )
    return None


def find_pointing(board: Board) -> Optional[Step]:
    """Pointing pair/triple: in a box, all cells with digit d lie on one line."""
    for b_idx, box in enumerate(BOXES):
        for d in range(1, 10):
            bm = 1 << (d - 1)
            places = [i for i in box if board.cells[i] == 0 and board.candidates[i] & bm]
            if len(places) < 2:
                continue
            rows_used = {i // 9 for i in places}
            cols_used = {i % 9 for i in places}
            if len(rows_used) == 1:
                r = next(iter(rows_used))
                elims = []
                for c in range(9):
                    idx = r * 9 + c
                    if idx in places:
                        continue
                    if board.cells[idx] == 0 and (board.candidates[idx] & bm):
                        elims.append((idx, d))
                if elims:
                    return Step(
                        technique=Technique.POINTING,
                        focus_cells=places,
                        affected_cells=sorted({c for c, _ in elims}),
                        eliminations=elims,
                        digits=[d],
                        explanation_en=(
                            f"Pointing: in box {b_idx+1}, digit {d} can only go "
                            f"on row {r+1}, so it is eliminated from the rest of that row."
                        ),
                        explanation_fr=(
                            f"Paire/triplet pointant : dans la boîte {b_idx+1}, "
                            f"le chiffre {d} ne peut aller que sur la ligne {r+1}, "
                            f"donc il est éliminé du reste de cette ligne."
                        ),
                    )
            if len(cols_used) == 1:
                c = next(iter(cols_used))
                elims = []
                for r in range(9):
                    idx = r * 9 + c
                    if idx in places:
                        continue
                    if board.cells[idx] == 0 and (board.candidates[idx] & bm):
                        elims.append((idx, d))
                if elims:
                    return Step(
                        technique=Technique.POINTING,
                        focus_cells=places,
                        affected_cells=sorted({c for c, _ in elims}),
                        eliminations=elims,
                        digits=[d],
                        explanation_en=(
                            f"Pointing: in box {b_idx+1}, digit {d} can only go "
                            f"on column {c+1}, so it is eliminated from the rest of that column."
                        ),
                        explanation_fr=(
                            f"Paire/triplet pointant : dans la boîte {b_idx+1}, "
                            f"le chiffre {d} ne peut aller que sur la colonne {c+1}, "
                            f"donc il est éliminé du reste de cette colonne."
                        ),
                    )
    return None


def find_box_line(board: Board) -> Optional[Step]:
    """Box/line reduction: digit d on a line is confined to one box."""
    for line_type, lines in (("row", ROWS), ("col", COLS)):
        for li, line in enumerate(lines):
            for d in range(1, 10):
                bm = 1 << (d - 1)
                places = [i for i in line if board.cells[i] == 0 and board.candidates[i] & bm]
                if len(places) < 2:
                    continue
                boxes_used = {((i // 9) // 3) * 3 + ((i % 9) // 3) for i in places}
                if len(boxes_used) != 1:
                    continue
                b_idx = next(iter(boxes_used))
                elims = []
                for idx in BOXES[b_idx]:
                    if idx in places:
                        continue
                    if board.cells[idx] == 0 and (board.candidates[idx] & bm):
                        elims.append((idx, d))
                if elims:
                    name_en = f"{line_type} {li+1}"
                    name_fr = ("ligne " if line_type == "row" else "colonne ") + str(li + 1)
                    return Step(
                        technique=Technique.BOX_LINE,
                        focus_cells=places,
                        affected_cells=sorted({c for c, _ in elims}),
                        eliminations=elims,
                        digits=[d],
                        explanation_en=(
                            f"Box/line reduction: on {name_en}, digit {d} lies "
                            f"only in box {b_idx+1}, so it is eliminated from "
                            f"the rest of that box."
                        ),
                        explanation_fr=(
                            f"Réduction ligne/boîte : sur la {name_fr}, le chiffre {d} "
                            f"ne se trouve que dans la boîte {b_idx+1}, donc il est "
                            f"éliminé du reste de cette boîte."
                        ),
                    )
    return None


def find_x_wing(board: Board) -> Optional[Step]:
    """X-Wing: digit d forms a 2x2 rectangle on two rows (or columns)."""
    for d in range(1, 10):
        bm = 1 << (d - 1)
        # Row-based
        row_cols: list[list[int]] = []
        for r in range(9):
            cols = [c for c in range(9) if board.cells[r * 9 + c] == 0 and board.candidates[r * 9 + c] & bm]
            row_cols.append(cols)
        for r1, r2 in combinations(range(9), 2):
            if len(row_cols[r1]) == 2 and row_cols[r1] == row_cols[r2]:
                c1, c2 = row_cols[r1]
                focus = [r1 * 9 + c1, r1 * 9 + c2, r2 * 9 + c1, r2 * 9 + c2]
                elims = []
                for r in range(9):
                    if r in (r1, r2):
                        continue
                    for c in (c1, c2):
                        idx = r * 9 + c
                        if board.cells[idx] == 0 and board.candidates[idx] & bm:
                            elims.append((idx, d))
                if elims:
                    return Step(
                        technique=Technique.X_WING,
                        focus_cells=focus,
                        affected_cells=sorted({c for c, _ in elims}),
                        eliminations=elims,
                        digits=[d],
                        explanation_en=(
                            f"X-Wing on digit {d}: rows {r1+1} and {r2+1} both "
                            f"restrict {d} to columns {c1+1} and {c2+1}, so {d} "
                            f"is eliminated from these columns elsewhere."
                        ),
                        explanation_fr=(
                            f"X-Wing sur le chiffre {d} : les lignes {r1+1} et {r2+1} "
                            f"limitent toutes deux {d} aux colonnes {c1+1} et {c2+1}, "
                            f"donc {d} est éliminé ailleurs dans ces colonnes."
                        ),
                    )
        # Column-based
        col_rows: list[list[int]] = []
        for c in range(9):
            rows = [r for r in range(9) if board.cells[r * 9 + c] == 0 and board.candidates[r * 9 + c] & bm]
            col_rows.append(rows)
        for c1, c2 in combinations(range(9), 2):
            if len(col_rows[c1]) == 2 and col_rows[c1] == col_rows[c2]:
                r1, r2 = col_rows[c1]
                focus = [r1 * 9 + c1, r1 * 9 + c2, r2 * 9 + c1, r2 * 9 + c2]
                elims = []
                for c in range(9):
                    if c in (c1, c2):
                        continue
                    for r in (r1, r2):
                        idx = r * 9 + c
                        if board.cells[idx] == 0 and board.candidates[idx] & bm:
                            elims.append((idx, d))
                if elims:
                    return Step(
                        technique=Technique.X_WING,
                        focus_cells=focus,
                        affected_cells=sorted({c for c, _ in elims}),
                        eliminations=elims,
                        digits=[d],
                        explanation_en=(
                            f"X-Wing on digit {d}: columns {c1+1} and {c2+1} both "
                            f"restrict {d} to rows {r1+1} and {r2+1}, so {d} is "
                            f"eliminated from these rows elsewhere."
                        ),
                        explanation_fr=(
                            f"X-Wing sur le chiffre {d} : les colonnes {c1+1} et {c2+1} "
                            f"limitent toutes deux {d} aux lignes {r1+1} et {r2+1}, "
                            f"donc {d} est éliminé ailleurs dans ces lignes."
                        ),
                    )
    return None


# Order matters: cheaper techniques first
TECHNIQUE_FINDERS: list[tuple[Technique, Callable[[Board], Optional[Step]]]] = [
    (Technique.NAKED_SINGLE, find_naked_single),
    (Technique.HIDDEN_SINGLE, find_hidden_single),
    (Technique.NAKED_PAIR, find_naked_pair),
    (Technique.HIDDEN_PAIR, find_hidden_pair),
    (Technique.NAKED_TRIPLE, find_naked_triple),
    (Technique.POINTING, find_pointing),
    (Technique.BOX_LINE, find_box_line),
    (Technique.X_WING, find_x_wing),
]


# ---------------------------------------------------------------------------
# Human solver driver
# ---------------------------------------------------------------------------


class HumanSolver:
    """Applies techniques iteratively to solve a board.

    Returns the ordered list of steps. If no technique applies and the board
    is not yet solved, stops (the puzzle requires harder logic or guessing).
    """

    def next_step(self, board: Board) -> Optional[Step]:
        for _, finder in TECHNIQUE_FINDERS:
            step = finder(board)
            if step:
                return step
        return None

    def solve(self, board: Board, max_steps: int = 500) -> tuple[Board, list[Step]]:
        work = board.copy()
        work.recompute_candidates()
        steps: list[Step] = []
        for _ in range(max_steps):
            if work.is_complete():
                break
            step = self.next_step(work)
            if step is None:
                break
            apply_step(work, step)
            steps.append(step)
        return work, steps

    def hardest_technique(self, board: Board) -> Optional[Technique]:
        _, steps = self.solve(board)
        if not steps:
            return None
        return max(steps, key=lambda s: TECHNIQUE_DIFFICULTY[s.technique]).technique


def apply_step(board: Board, step: Step) -> None:
    """Apply a step's placement or eliminations to the board."""
    if step.placement:
        idx, d = step.placement
        board.place(idx, d)
    for idx, d in step.eliminations:
        board.candidates[idx] &= ~(1 << (d - 1))

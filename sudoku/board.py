"""Sudoku board representation.

Uses an 81-cell array of integers (0 = empty, 1..9 = filled) plus a
bitmask-based candidate tracker for fast constraint propagation.

Cell indices: row * 9 + col, 0..80.
Unit indices: 0..8 rows, 0..8 cols, 0..8 boxes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


ALL_MASK = 0x1FF  # bits 0..8 set (candidates 1..9)


def _build_peer_tables():
    """Precompute row/col/box unit indices and peer sets for each cell."""
    rows = [[r * 9 + c for c in range(9)] for r in range(9)]
    cols = [[r * 9 + c for r in range(9)] for c in range(9)]
    boxes = [[] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            b = (r // 3) * 3 + (c // 3)
            boxes[b].append(r * 9 + c)

    units_of = [[] for _ in range(81)]
    peers = [set() for _ in range(81)]
    for r in range(9):
        for c in range(9):
            idx = r * 9 + c
            b = (r // 3) * 3 + (c // 3)
            units_of[idx] = [rows[r], cols[c], boxes[b]]
            for unit in units_of[idx]:
                for j in unit:
                    if j != idx:
                        peers[idx].add(j)
    return rows, cols, boxes, units_of, [frozenset(p) for p in peers]


ROWS, COLS, BOXES, UNITS_OF, PEERS = _build_peer_tables()
ALL_UNITS = ROWS + COLS + BOXES  # 27 units of 9 cells each


def bit(value: int) -> int:
    """Return the bitmask for digit 1..9."""
    return 1 << (value - 1)


def bits_to_digits(mask: int) -> list[int]:
    """Return the digits (1..9) set in the mask."""
    return [d for d in range(1, 10) if mask & (1 << (d - 1))]


def popcount(mask: int) -> int:
    return bin(mask).count("1")


@dataclass
class Board:
    """Mutable 9x9 sudoku grid with candidate tracking.

    cells: list of 81 ints (0 empty, 1..9 filled).
    candidates: list of 81 bitmasks (bit d-1 set means digit d is possible).
                For filled cells, the mask is 0.
    givens: set of indices that were part of the initial puzzle.
    """

    cells: list[int] = field(default_factory=lambda: [0] * 81)
    candidates: list[int] = field(default_factory=lambda: [ALL_MASK] * 81)
    givens: set[int] = field(default_factory=set)

    # ---- Construction ----

    @classmethod
    def from_string(cls, s: str, givens_from_nonzero: bool = True) -> "Board":
        """Parse a 81-char string. '0' or '.' = empty, '1'..'9' = filled.

        Ignores whitespace and common separators.
        """
        clean = []
        for ch in s:
            if ch.isdigit():
                clean.append(ch)
            elif ch == ".":
                clean.append("0")
        if len(clean) != 81:
            raise ValueError(
                f"Expected 81 digits/dots, got {len(clean)}"
            )
        b = cls()
        for i, ch in enumerate(clean):
            v = int(ch)
            if v:
                b.cells[i] = v
                b.candidates[i] = 0
                if givens_from_nonzero:
                    b.givens.add(i)
        b.recompute_candidates()
        return b

    def to_string(self, empty: str = "0") -> str:
        return "".join(str(v) if v else empty for v in self.cells)

    def copy(self) -> "Board":
        b = Board(
            cells=self.cells[:],
            candidates=self.candidates[:],
            givens=set(self.givens),
        )
        return b

    # ---- Queries ----

    def is_complete(self) -> bool:
        return all(v != 0 for v in self.cells)

    def empty_cells(self) -> list[int]:
        return [i for i, v in enumerate(self.cells) if v == 0]

    def is_valid(self) -> bool:
        """Check that filled cells don't conflict in any unit."""
        for unit in ALL_UNITS:
            seen = 0
            for idx in unit:
                v = self.cells[idx]
                if v == 0:
                    continue
                m = 1 << (v - 1)
                if seen & m:
                    return False
                seen |= m
        return True

    def conflicts(self) -> set[int]:
        """Return indices of cells that conflict with a peer."""
        bad = set()
        for unit in ALL_UNITS:
            counts: dict[int, list[int]] = {}
            for idx in unit:
                v = self.cells[idx]
                if v:
                    counts.setdefault(v, []).append(idx)
            for v, idxs in counts.items():
                if len(idxs) > 1:
                    bad.update(idxs)
        return bad

    # ---- Mutation ----

    def recompute_candidates(self) -> None:
        """Rebuild candidate masks from scratch based on current cell values."""
        for i in range(81):
            if self.cells[i]:
                self.candidates[i] = 0
                continue
            mask = ALL_MASK
            for p in PEERS[i]:
                v = self.cells[p]
                if v:
                    mask &= ~(1 << (v - 1))
            self.candidates[i] = mask

    def place(self, idx: int, value: int) -> None:
        """Place a value and update peer candidates."""
        self.cells[idx] = value
        self.candidates[idx] = 0
        bm = ~(1 << (value - 1))
        for p in PEERS[idx]:
            self.candidates[p] &= bm

    def clear(self, idx: int) -> None:
        """Clear a cell (use recompute_candidates afterwards)."""
        self.cells[idx] = 0

    def candidates_of(self, idx: int) -> list[int]:
        return bits_to_digits(self.candidates[idx])

    # ---- Display ----

    def pretty(self) -> str:
        lines = []
        for r in range(9):
            if r % 3 == 0:
                lines.append("+-------+-------+-------+")
            row_parts = []
            for c in range(9):
                if c % 3 == 0:
                    row_parts.append("|")
                v = self.cells[r * 9 + c]
                row_parts.append(str(v) if v else ".")
            row_parts.append("|")
            lines.append(" ".join(row_parts))
        lines.append("+-------+-------+-------+")
        return "\n".join(lines)

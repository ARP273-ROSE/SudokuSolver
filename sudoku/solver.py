"""Fast sudoku solver using constraint propagation + backtracking with MRV.

This solver is used whenever we need a raw solution (generator, quick solve).
For step-by-step human-style solving and hints, see `techniques.HumanSolver`.

Algorithm:
  1. Propagate: apply naked singles (cells with one candidate) and hidden
     singles (a digit with only one possible cell in a unit), repeatedly.
  2. If the puzzle is not solved, pick the empty cell with the fewest
     candidates (Minimum Remaining Values heuristic) and try each candidate
     via recursive search.
  3. Detect multiple solutions by continuing after finding the first one,
     up to a configurable limit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .board import (
    ALL_MASK,
    ALL_UNITS,
    Board,
    PEERS,
    bits_to_digits,
    popcount,
)


@dataclass
class SolveResult:
    solutions: list[Board]
    propagations: int = 0
    guesses: int = 0
    timed_out: bool = False

    @property
    def solved(self) -> bool:
        return len(self.solutions) >= 1

    @property
    def unique(self) -> bool:
        return len(self.solutions) == 1


class Solver:
    """Bitmask-based backtracking solver.

    max_nodes caps the combined propagation + guess budget. When exceeded,
    the search stops and `SolveResult.timed_out` is set — this protects the
    UI against malformed or hostile input that would otherwise hang.
    """

    def __init__(self, max_solutions: int = 2, max_nodes: int = 2_000_000):
        self.max_solutions = max_solutions
        self.max_nodes = max_nodes
        self._nodes = 0

    # ---- Public API ----

    def solve(self, board: Board) -> SolveResult:
        work = board.copy()
        work.recompute_candidates()
        result = SolveResult(solutions=[])
        self._nodes = 0
        if not self._propagate(work, result):
            return result
        self._search(work, result)
        return result

    def has_unique_solution(self, board: Board) -> bool:
        saved = self.max_solutions
        self.max_solutions = 2
        try:
            res = self.solve(board)
        finally:
            self.max_solutions = saved
        return res.unique

    # ---- Core ----

    def _propagate(self, board: Board, result: SolveResult) -> bool:
        """Repeatedly apply naked/hidden singles until stable.

        Returns False if a contradiction is found or node budget exhausted.
        """
        changed = True
        while changed:
            if self._nodes > self.max_nodes:
                result.timed_out = True
                return False
            self._nodes += 1
            changed = False

            # Naked singles: cell with exactly one candidate
            for i in range(81):
                if board.cells[i]:
                    continue
                m = board.candidates[i]
                if m == 0:
                    return False  # empty cell with no candidates
                if popcount(m) == 1:
                    d = m.bit_length()  # bit k+1 -> digit k+1
                    board.place(i, d)
                    result.propagations += 1
                    changed = True

            # Hidden singles: a digit that has only one possible cell in a unit
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
                                spot = -2  # more than one possible
                                break
                    if already:
                        continue
                    if spot == -1:
                        return False  # digit has no place in this unit
                    if spot >= 0:
                        board.place(spot, d)
                        result.propagations += 1
                        changed = True
        return True

    def _search(self, board: Board, result: SolveResult) -> None:
        if len(result.solutions) >= self.max_solutions:
            return
        if result.timed_out or self._nodes > self.max_nodes:
            result.timed_out = True
            return
        self._nodes += 1

        # Find cell with minimum remaining values
        best = -1
        best_count = 10
        for i in range(81):
            if board.cells[i] == 0:
                c = popcount(board.candidates[i])
                if c < best_count:
                    best_count = c
                    best = i
                    if c <= 1:
                        break

        if best == -1:
            # Solved
            result.solutions.append(board.copy())
            return

        if best_count == 0:
            return

        for d in bits_to_digits(board.candidates[best]):
            trial = board.copy()
            trial.place(best, d)
            result.guesses += 1
            if self._propagate(trial, result):
                self._search(trial, result)
            if len(result.solutions) >= self.max_solutions:
                return

"""Sudoku puzzle generator.

Strategy:
  1. Build a random fully-solved board (backtracking with randomized digits).
  2. Remove clues one at a time (symmetrically when possible), each time
     verifying that the resulting puzzle still has a unique solution.
  3. Stop when reaching the target clue count or when no more removals are
     possible without breaking uniqueness.
  4. Rate the puzzle by which is the hardest human technique required to
     solve it (via `HumanSolver`) — if the difficulty doesn't match, retry.

Difficulty levels are expressed both by clue count and by required technique:

  EASY    : 36-45 clues, only naked/hidden singles
  MEDIUM  : 30-35 clues, up to naked pair / hidden pair
  HARD    : 26-32 clues, up to pointing / box-line
  EXPERT  : 22-28 clues, X-Wing required, backtracking allowed as fallback

These are heuristics — the generator retries until a puzzle matches.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .board import ALL_MASK, Board
from .solver import Solver
from .techniques import (
    HumanSolver,
    TECHNIQUE_DIFFICULTY,
    Technique,
)


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


DIFFICULTY_PROFILE = {
    Difficulty.EASY: {
        "min_clues": 36,
        "max_clues": 45,
        "max_technique": Technique.HIDDEN_SINGLE,
        "min_technique": Technique.NAKED_SINGLE,
    },
    Difficulty.MEDIUM: {
        "min_clues": 30,
        "max_clues": 35,
        "max_technique": Technique.HIDDEN_PAIR,
        "min_technique": Technique.HIDDEN_SINGLE,
    },
    Difficulty.HARD: {
        "min_clues": 26,
        "max_clues": 32,
        "max_technique": Technique.BOX_LINE,
        "min_technique": Technique.NAKED_PAIR,
    },
    Difficulty.EXPERT: {
        "min_clues": 22,
        "max_clues": 28,
        "max_technique": Technique.X_WING,
        "min_technique": Technique.BOX_LINE,
    },
}


@dataclass
class GeneratedPuzzle:
    puzzle: Board
    solution: Board
    difficulty: Difficulty
    clue_count: int
    hardest_technique: Optional[Technique]


class Generator:
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.solver = Solver(max_solutions=2)
        self.human = HumanSolver()

    # ---- Full solution generation ----

    def random_solution(self) -> Board:
        """Generate a random complete sudoku via shuffled backtracking."""
        board = Board()
        self._fill(board, 0)
        return board

    def _fill(self, board: Board, pos: int) -> bool:
        if pos == 81:
            return True
        if board.cells[pos]:
            return self._fill(board, pos + 1)
        digits = list(range(1, 10))
        self.rng.shuffle(digits)
        r, c = divmod(pos, 9)
        for d in digits:
            if self._safe(board, r, c, d):
                board.cells[pos] = d
                if self._fill(board, pos + 1):
                    return True
                board.cells[pos] = 0
        return False

    @staticmethod
    def _safe(board: Board, r: int, c: int, d: int) -> bool:
        for i in range(9):
            if board.cells[r * 9 + i] == d:
                return False
            if board.cells[i * 9 + c] == d:
                return False
        br, bc = (r // 3) * 3, (c // 3) * 3
        for dr in range(3):
            for dc in range(3):
                if board.cells[(br + dr) * 9 + bc + dc] == d:
                    return False
        return True

    # ---- Clue removal ----

    def _dig_holes(self, solution: Board, target_clues: int, symmetric: bool = True) -> Board:
        puzzle = solution.copy()
        puzzle.givens = set(range(81))
        indices = list(range(81))
        self.rng.shuffle(indices)

        clues = 81
        for idx in indices:
            if clues <= target_clues:
                break
            pair = 80 - idx if symmetric else None
            if puzzle.cells[idx] == 0:
                continue
            saved = puzzle.cells[idx]
            saved_pair = puzzle.cells[pair] if pair is not None and pair != idx else None

            puzzle.cells[idx] = 0
            if pair is not None and pair != idx and saved_pair:
                puzzle.cells[pair] = 0

            puzzle.recompute_candidates()
            test = Board(
                cells=puzzle.cells[:],
                candidates=puzzle.candidates[:],
                givens=set(),
            )
            if self.solver.has_unique_solution(test):
                clues -= 1
                if pair is not None and pair != idx and saved_pair:
                    clues -= 1
            else:
                puzzle.cells[idx] = saved
                if pair is not None and pair != idx and saved_pair:
                    puzzle.cells[pair] = saved_pair

        puzzle.givens = {i for i, v in enumerate(puzzle.cells) if v}
        puzzle.recompute_candidates()
        return puzzle

    # ---- Difficulty-matched generation ----

    def generate(self, difficulty: Difficulty, max_attempts: int = 40) -> GeneratedPuzzle:
        profile = DIFFICULTY_PROFILE[difficulty]
        target = self.rng.randint(profile["min_clues"], profile["max_clues"])
        best: Optional[GeneratedPuzzle] = None

        for _ in range(max_attempts):
            solution = self.random_solution()
            puzzle = self._dig_holes(solution, target, symmetric=True)
            clue_count = sum(1 for v in puzzle.cells if v)
            hardest = self.human.hardest_technique(puzzle)

            if self._matches(difficulty, clue_count, hardest):
                return GeneratedPuzzle(
                    puzzle=puzzle,
                    solution=solution,
                    difficulty=difficulty,
                    clue_count=clue_count,
                    hardest_technique=hardest,
                )
            # Keep the closest one as fallback
            if best is None:
                best = GeneratedPuzzle(
                    puzzle=puzzle,
                    solution=solution,
                    difficulty=difficulty,
                    clue_count=clue_count,
                    hardest_technique=hardest,
                )

        assert best is not None
        return best

    def _matches(
        self,
        difficulty: Difficulty,
        clue_count: int,
        hardest: Optional[Technique],
    ) -> bool:
        profile = DIFFICULTY_PROFILE[difficulty]
        if not (profile["min_clues"] <= clue_count <= profile["max_clues"]):
            return False
        if hardest is None:
            return difficulty == Difficulty.EASY
        max_d = TECHNIQUE_DIFFICULTY[profile["max_technique"]]
        min_d = TECHNIQUE_DIFFICULTY[profile["min_technique"]]
        h = TECHNIQUE_DIFFICULTY[hardest]
        return min_d <= h <= max_d

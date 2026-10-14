# -*- coding: utf-8 -*-
"""Le moteur : une grille générée a une solution unique, que le solveur trouve."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sudoku import Board, Difficulty, Generator, Solver  # noqa: E402

GRILLE = ("530070000600195000098000060800060003400803001"
          "700020006060000280000419005000080079")


def test_grille_classique():
    r = Solver().solve(Board.from_string(GRILLE))
    assert r.solved and r.unique
    sol = r.solutions[0]
    assert sol.is_complete() and sol.is_valid()
    assert sol.to_string().startswith("534678912")


def test_generation_solution_unique():
    gen = Generator(seed=7)
    for d in (Difficulty.EASY, Difficulty.MEDIUM):
        gp = gen.generate(d)
        board = getattr(gp, 'puzzle', None) or getattr(gp, 'board')
        assert Solver().has_unique_solution(board)

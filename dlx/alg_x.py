"""Implementation of Donald Knuth's Algorithm X.

See http://arxiv.org/abs/cs/0011047.
"""

from collections.abc import Mapping, Sequence
from typing import Protocol

from .dlmatrix import Cell, DancingLinksMatrix, iterate_cell

__author__ = "Davide Canton"


class SolveCallback(Protocol):
    def __call__(self, solution: Mapping[int, Sequence[str]]) -> bool: ...


class AlgorithmX:
    """Callable object implementing the Algorithm X."""

    sol_dict: dict[int, Cell]
    stop: bool
    matrix: DancingLinksMatrix
    callback: SolveCallback
    choose_min: bool

    def __init__(
        self, matrix: DancingLinksMatrix, callback: SolveCallback, choose_min: bool = True
    ) -> None:
        """Creates an Algorithm_X object that solves the problem encoded in matrix.

        Args:
            matrix (DancingLinksMatrix): The ``DancingLinksMatrix`` instance.

            callback (Callable): The callback called on every solution. callback has to
            be a function receiving a dict argument ``{row_index: linked list of the row}``,
            and can return a ``bool`` value. The solver keeps going on until the callback returns
            ``True``.

            choose_min (bool): If ``True``, the column with the minimum number of 1s is
            chosen at each iteration, if ``False`` a random column is chosen.
        """
        self.sol_dict = {}
        self.stop = False
        self.matrix = matrix
        self.callback = callback
        self.choose_min = choose_min

    def solve(self) -> None:
        """Starts the search."""
        self._search(0)

    def _search(self, k: int) -> None:
        # print(f"Size: {k}")
        # print(f"Solution: {self.sol_dict}")
        # print("Matrix:")
        # print(self.matrix)

        if self.matrix.header.R == self.matrix.header:
            # matrix is empty, solution found
            if self.callback(self._create_sol(k)):
                self.stop = True
            return

        if self.choose_min:
            col = self.matrix.min_column()
        else:
            col = self.matrix.random_column()

        # cover column col
        self.matrix.cover(col)
        row = col.D

        for row in iterate_cell(col, "D"):
            self.sol_dict[k] = row

            # cover the columns pointed by the 1s in the chosen row
            for j in iterate_cell(row, "R"):
                self.matrix.cover(j.C)

            self._search(k + 1)
            if self.stop:
                return

            # uncover columns
            row = self.sol_dict[k]
            col = row.C

            for j in iterate_cell(row, "L"):
                self.matrix.uncover(j.C)

        self.matrix.uncover(col)

    def _create_sol(self, k: int) -> Mapping[int, Sequence[str]]:
        # creates a solution from the inner dict
        sol = {}

        for key, row in self.sol_dict.items():
            if key >= k:
                continue

            sol[row.indexes[0]] = [row.C.name] + [r.C.name for r in iterate_cell(row, "R")]

        return sol

"""
Implementation of Donald Knuth's Algorithm X
(http://arxiv.org/abs/cs/0011047).
"""

import string

from .dlmatrix import DancingLinksMatrix, iterate_cell

__author__ = "Davide Canton"


class AlgorithmX:
    """Callable object implementing the Algorithm X."""

    def __init__(self, matrix, callback, choose_min=True):
        """
        Creates an Algorithm_X object that solves the problem
        encoded in matrix.

        :param matrix: The DL_Matrix instance.
        :param callback: The callback called on every solution. callback has to
                         be a function receiving a dict argument
                         {row_index: linked list of the row}, and can return a
                         bool value. The solver keeps going on until the
                         callback returns a True value.

        :param choose_min: If True, the column with the minimum number of 1s is
                           chosen at each iteration, if False a random column is
                           chosen.
        """
        self.sol_dict = {}
        self.stop = False
        self.matrix = matrix
        self.callback = callback
        self.choose_min = choose_min

    def __call__(self):
        """Starts the search."""
        self._search(0)

    def _search(self, k):
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

    def _create_sol(self, k):
        # creates a solution from the inner dict
        sol = {}
        for key, row in self.sol_dict.items():
            if key >= k:
                continue

            tmp_list = [row.C.name]
            tmp_list.extend(r.C.name for r in iterate_cell(row, "R"))
            sol[row.indexes[0]] = tmp_list

        return sol


def main():
    def from_dense(row):
        return [i for i, el in enumerate(row) if el]

    rows = [
        from_dense([0, 0, 1, 0, 1, 1, 0]),
        from_dense([1, 0, 0, 1, 0, 0, 1]),
        from_dense([0, 1, 1, 0, 0, 1, 0]),
        from_dense([1, 0, 0, 1, 0, 0, 0]),
        from_dense([0, 1, 0, 0, 0, 0, 1]),
        from_dense([0, 0, 0, 1, 1, 0, 1]),
    ]

    size = max(max(rows, key=max)) + 1

    d = DancingLinksMatrix(string.ascii_uppercase[:size])

    for row in rows:
        d.add_sparse_row(row, already_sorted=True)

    # print(d)

    AlgorithmX(d, print)()


if __name__ == "__main__":
    main()

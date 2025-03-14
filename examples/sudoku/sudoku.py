"""Sudoku Solver using Dancing Links."""

import itertools as it
import sys

import numpy as np

from dlx import AlgorithmX, DancingLinksMatrix

from .sudoku_board import SudokuBoard

__author__ = "Davide Canton"


def column_names():
    """Yields the column names."""
    # 81, RiCj = j + 9i
    for i, j in it.product(range(1, 10), repeat=2):
        yield f"R{i}C{j}"
    # 81, Ri#v = v + 9i
    for i, j in it.product(range(1, 10), repeat=2):
        yield f"R{i}#{j}"
    # 81, Cj#v = v + 9j
    for i, j in it.product(range(1, 10), repeat=2):
        yield f"C{i}#{j}"
    # 81, Bn#v = v + 9n
    for i, j in it.product(range(1, 10), repeat=2):
        yield f"B{i}#{j}"


def get_square_index(i: int, j: int):
    """Returns the square index."""
    i, j = i // 3, j // 3
    return 3 * i + j


def compute_row(i: int, j: int, v: int):
    """Computes the row indexes."""
    i -= 1
    j -= 1
    v -= 1
    i1 = j + 9 * i
    i2 = 81 + v + 9 * i
    i3 = 81 * 2 + v + 9 * j
    i4 = 81 * 3 + v + 9 * get_square_index(i, j)
    return [i1, i2, i3, i4]


class GetFirstSol:
    """Callable that returns the first solution."""

    def __init__(self):
        """Init."""
        self.sol = None

    def __call__(self, sol):
        """Returns the solved matrix."""
        matrix = np.zeros((9, 9), dtype=np.uint8)

        for v in sol.values():
            i, j, val = 0, 0, 0
            for el in v:
                if el[2] == "#":
                    val = int(el[3])
                else:
                    i, j = map(int, [el[1], el[3]])
            matrix[i - 1, j - 1] = val

        self.sol = matrix
        return True


class CountSolutions:
    """Callable that counts the solutions."""

    def __init__(self):
        """Init."""
        self.count = 0

    def __call__(self, _sol):
        """Count solutions."""
        self.count += 1


def read_from_file(file_path) -> dict[tuple[int, int], int]:
    """Reads a sudoku matrix from a file."""
    known = {}
    with open(file_path) as f_in:
        for i, line in enumerate(f_in, start=1):
            for j, char in enumerate(line.rstrip(), start=1):
                try:
                    known[i, j] = int(char)
                except ValueError:
                    pass
    return known


def to_np(known):
    """Converts a sparse matrix dict into a numpy array."""
    matrix = np.zeros((9, 9), dtype=np.uint8)

    for (i, j), v in known.items():
        matrix[i - 1, j - 1] = v

    return matrix


def main():
    """Main solver."""
    matrix = DancingLinksMatrix(column_names())

    known = read_from_file(sys.argv[1])
    # starting_board = SudokuBoard(to_np(known))
    # print(starting_board)

    for i, j in it.product(range(1, 10), repeat=2):
        if (i, j) in known:
            row = compute_row(i, j, known[i, j])
            matrix.add_sparse_row(row, already_sorted=True)
        else:
            for v in range(1, 10):
                row = compute_row(i, j, v)
                matrix.add_sparse_row(row, already_sorted=True)

    matrix.end_add()

    # sol = CountSolutions()
    sol = GetFirstSol()

    try:
        alg = AlgorithmX(matrix, sol)
        alg.solve()
        board = SudokuBoard(sol.sol)
        print(board)
        print(board.valid())
    finally:
        # print(sol.count)
        pass


if __name__ == "__main__":
    main()

"""
N-queens solver using Dancing Links.
"""

from dlmatrix import DancingLinksMatrix
from alg_x import AlgorithmX

__author__ = 'Davide Canton'


def get_names(n):
    for i in range(n):
        yield f"R{i}"
    for i in range(n):
        yield f"F{i}"
    for i in range(2 * n - 1):
        yield f"A{i}", False  # secondary column
    for i in range(2 * n - 1):
        yield f"B{i}", False  # secondary column


def compute_row(i, j, n):
    # R is 0 .. N-1
    # F is N .. 2*N-1
    # A is 2*N .. 4*N - 2
    # B is 4*N - 1 .. 6*N - 3
    return [i, n + j, 2 * n + i + j, 5 * n - 2 - i + j]


class PrintFirstSol:
    def __init__(self, size):
        self.size = size

    def __call__(self, sol):
        pos = [0] * self.size

        for v in sol.values():
            v.sort()
            c, r = map(int, [v[2][1:], v[3][1:]])
            pos[r] = c

        for i in range(self.size):
            r = [" "] * self.size
            r[pos[i]] = "O"
            inner = "|".join(r)
            print(f"|{inner}|")

        print()
        return True


def print_solution_count():
    count = 0

    def inner(*a):
        nonlocal count
        count += 1

    return inner


def main():
    size = 6

    d = DancingLinksMatrix(get_names(size))

    for i in range(size):
        for j in range(size):
            row = compute_row(i, j, size)
            d.add_sparse_row(row, already_sorted=True)

    d.end_add()

    p = PrintFirstSol(size)
    alg = AlgorithmX(d, p)
    alg()


if __name__ == "__main__":
    main()

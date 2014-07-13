__author__ = 'Kami'

from dl_matrix import DL_Matrix
from alg_x import Algorithm_X


def get_names(N):
    for i in range(N):
        yield "R{}".format(i)
    for i in range(N):
        yield "F{}".format(i)
    for i in range(2 * N - 1):
        yield "A{}".format(i), False
    for i in range(2 * N - 1):
        yield "B{}".format(i), False


def compute_row(i, j, N):
    # R is 0 .. N-1
    # F is N .. 2*N-1
    # A is 2*N .. 4*N - 2
    # B is 4*N - 1 .. 6*N - 3
    return [i, N + j, 2 * N + i + j, 5 * N - 2 - i + j]


class Print_Sol:
    def __init__(self, N):
        self.N = N
        self.count = 0

    def __call__(self, sol):
        print("Solution", self.count)
        pos = [0] * self.N
        for v in sol.values():
            v.sort()
            c, r = map(int, [v[2][1:], v[3][1:]])
            pos[r] = c
        for i in range(self.N):
            r = [" "] * self.N
            r[pos[i]] = "O"
            inner = "|".join(r)
            print("|{}|".format(inner))
        print()
        self.count += 1
        return True


class Print_Sol_Count:
    def __init__(self):
        self.count = 0

    def __call__(self, sol):
        self.count += 1


if __name__ == "__main__":
    N = 13

    d = DL_Matrix(get_names(N))

    for i in range(N):
        for j in range(N):
            row = compute_row(i, j, N)
            d.add_sparse_row(row, already_sorted=True)
    d.end_add()

    p = Print_Sol_Count()
    Algorithm_X(d, p)()
    print("Solution count:", p.count)
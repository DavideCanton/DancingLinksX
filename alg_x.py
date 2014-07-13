__author__ = 'Kami'

from dl_matrix import DL_Matrix


class Algorithm_X:
    def __init__(self, matrix, callback, choose_min=True):
        self.O = {}
        self.stop = False
        self.matrix = matrix
        self.callback = callback
        self.choose_min = choose_min

    def __call__(self):
        self._search(0)

    def _search(self, k):
        if self.matrix.header.R == self.matrix.header:
            if self.callback(self.create_sol(k)):
                self.stop = True
            return

        if self.choose_min:
            col = self.matrix.min_column()
        else:
            col = self.matrix.random_column()
        self.matrix.cover(col)
        row = col.D
        while row is not col:
            self.O[k] = row
            j = row.R
            while j is not row:
                self.matrix.cover(j.C)
                j = j.R
            self._search(k + 1)
            if self.stop:
                return
            row = self.O[k]
            col = row.C
            j = row.L
            while j is not row:
                self.matrix.uncover(j.C)
                j = j.L
            row = row.D
        self.matrix.uncover(col)

    def create_sol(self, k):
        sol = {}
        for key, row in self.O.items():
            if key >= k:
                continue
            tmp_list = []
            start = row
            tmp_list.append(row.C.N)
            row = row.R
            while row is not start:
                tmp_list.append(row.C.N)
                row = row.R
            sol[row.indexes[0]] = tmp_list
        return sol


if __name__ == "__main__":
    def from_dense(row):
        return [i for i, el in enumerate(row) if el]

    r = [from_dense([0, 0, 1, 0, 1, 1, 0]),
         from_dense([1, 0, 0, 1, 0, 0, 1]),
         from_dense([0, 1, 1, 0, 0, 1, 0]),
         from_dense([1, 0, 0, 1, 0, 0, 0]),
         from_dense([0, 1, 0, 0, 0, 0, 1]),
         from_dense([0, 0, 0, 1, 1, 0, 1])]

    d = DL_Matrix("ABCDEFG")

    # r = [from_dense([1, 0, 1]), from_dense([0, 1, 1]),
    # from_dense([1, 0, 0]), from_dense([0, 0, 1]),
    # from_dense([1, 1, 1])]
    # d = DL_Matrix("ABC")

    for row in r:
        d.add_sparse_row(row, already_sorted=True)

    # print(d)

    Algorithm_X(d, print)()
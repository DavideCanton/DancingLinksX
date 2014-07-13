__author__ = 'Kami'

import random
import numpy as np


class Cell:
    __slots__ = list("UDLRC") + ["indexes"]

    def __init__(self):
        self.U = self.D = self.L = self.R = self
        self.C = None
        self.indexes = None

    def __str__(self):
        return "Node: {}".format(self.indexes)


class HeaderCell(Cell):
    __slots__ = list("SN")

    def __init__(self, name):
        super(HeaderCell, self).__init__()
        self.S = 0
        self.N = name


class DL_Matrix:
    def __init__(self, columns=None):
        self.header = HeaderCell("H")
        self.nrows = self.ncols = 0
        self.col_list = []

        self.create_column_headers(columns)

    def create_column_headers(self, columns):
        if isinstance(columns, int):
            columns = int(columns)
            column_names = ("C{}".format(i) for i in range(columns))
        else:
            try:
                column_names = iter(columns)
            except TypeError:
                raise TypeError("Argument is not valid")

        prev = self.header
        for name in column_names:
            if isinstance(name, tuple):
                name, primary = name
            else:
                primary = True
            cell = HeaderCell(name)
            cell.indexes = (-1, self.ncols)
            self.col_list.append(cell)
            if primary:
                prev.R = cell
                cell.L = prev
                prev = cell
            self.ncols += 1

        prev.R = self.header
        self.header.L = prev

    def add_sparse_row(self, row, already_sorted=False):
        if self.col_list is None:
            raise RuntimeError("Unable to add")

        prev = None
        start = None

        if not already_sorted:
            row = sorted(row)

        for ind in row:
            cell = Cell()
            cell.indexes = (self.nrows, ind)

            if prev:
                prev.R = cell
                cell.L = prev
            else:
                start = cell

            col = self.col_list[ind]
            last = col.U
            last.D = cell
            cell.U = last
            col.U = cell
            cell.D = col
            cell.C = col
            col.S += 1
            prev = cell

        start.L = cell
        cell.R = start
        self.nrows += 1

    def end_add(self):
        self.col_list = None

    def min_column(self):
        col = self.header.R
        if col is self.header:
            raise ValueError("Empty matrix")

        col_min = col

        while col is not self.header:
            if col.S < col_min.S:
                col_min = col
            col = col.R

        return col_min

    def random_column(self):
        col = self.header.R
        if col is self.header:
            raise ValueError("Empty matrix")

        n = random.randint(0, self.ncols - 1)

        for _ in range(n):
            col = col.R

        if col == self.header:
            col = col.R
        return col

    def __str__(self):
        names = []
        m = np.zeros((self.nrows, self.ncols), dtype=np.uint8)
        col = self.header.R
        rows, cols = set(), []

        while col is not self.header:
            cols.append(col.indexes[1])
            names.append(col.N)
            cell = col.D
            while cell is not col:
                ind = cell.indexes
                rows.add(ind[0])
                m[ind] = 1
                cell = cell.D
            col = col.R

        m = m[list(rows)][:, cols]
        return "\n".join([", ".join(names), str(m)])

    def cover(self, c):
        # print("Cover column", c.N)
        c.R.L = c.L
        c.L.R = c.R
        i = c.D
        while i is not c:
            j = i.R
            while j is not i:
                j.D.U = j.U
                j.U.D = j.D
                j.C.S -= 1
                j = j.R
            i = i.D

    def uncover(self, c):
        # print("Uncover column", c.N)
        i = c.U
        while i is not c:
            j = i.L
            while j is not i:
                j.C.S += 1
                j.D.U = j.U.D = j
                j = j.L
            i = i.U
        c.R.L = c.L.R = c


if __name__ == "__main__":
    def from_dense(row):
        return [i for i, el in enumerate(row) if el]

    r = [from_dense([1, 0, 0, 1, 0, 0, 1]),
         from_dense([1, 0, 0, 1, 0, 0, 0]),
         from_dense([0, 0, 0, 1, 1, 0, 1]),
         from_dense([0, 0, 1, 0, 1, 1, 0]),
         from_dense([0, 1, 1, 0, 0, 1, 1]),
         from_dense([0, 1, 0, 0, 0, 0, 1])]

    d = DL_Matrix("1234567")

    for row in r:
        d.add_sparse_row(row, already_sorted=True)

    print(d.nrows)
    print(d.ncols)
    print(d)

    mc = d.min_column()
    print(mc)

    d.cover(mc)
    print(d)
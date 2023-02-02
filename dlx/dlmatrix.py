"""Implementation of Donald Knuth's Dancing Links Sparse Matrix
as a circular doubly linked list. (http://arxiv.org/abs/cs/0011047).
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from typing import Literal, Self

import numpy as np

__author__ = "Davide Canton"


class CannotAddRowsError(Exception):
    pass


class EmptyDLMatrix(Exception):
    pass


class Cell:
    """Inner cell, storing 4 pointers to neighbors, a pointer to the column header
    and the indexes associated.
    """

    U: Cell | None
    D: Cell | None
    L: Self | None
    R: Self | None
    C: HeaderCell | None
    indexes: tuple[int, int] | None

    __slots__ = list("UDLRC") + ["indexes"]

    def __init__(self) -> None:
        self.U = self.D = self.L = self.R = self
        self.C = None
        self.indexes = None

    def __str__(self) -> str:
        return f"Node: {self.indexes}"

    def __repr__(self) -> str:
        return f"Cell[{self.indexes}]"


class HeaderCell(Cell):
    """Column Header cell, a special cell that stores also a name and a size
    member.
    """

    size: int
    name: str
    is_first: bool

    __slots__ = ["size", "name", "is_first"]

    def __init__(self, name: str) -> str:
        super().__init__()
        self.size = 0
        self.name = name
        self.is_first = False


class DancingLinksMatrix:
    """Dancing Links sparse matrix implementation.
    It stores a circular doubly linked list of 1s, and another list
    of column headers. Every cell points to its upper, lower, left and right
    neighbors in a circular fashion.
    """

    header: HeaderCell
    rows: int
    cols: int
    col_list: list[HeaderCell] | None

    def __init__(self, columns: int | Iterable[str]):
        """Creates a DL_Matrix.

        :param columns: it can be an integer or an iterable. If columns is an
                        integer, columns columns are added to the matrix,
                        named C0,...,CN where N = columns -1. If columns is an
                        iterable, the number of columns and the names are
                        deduced from the iterable, else TypeError is raised.
                        The iterable may yield the names, or a tuple
                        (name,primary). primary is a bool value that is True
                        if the column is a primary one. If not specified, is
                        assumed that the column is a primary one.
        :raises TypeError, if columns is not a number neither an iterable.
        """
        self.header = HeaderCell("<H>")
        self.header.is_first = True
        self.rows = self.cols = 0
        self.col_list = []
        self._create_column_headers(columns)

    def _create_column_headers(self, columns: int | Iterable[str | tuple[str, bool]]):
        if isinstance(columns, int):
            columns = int(columns)
            column_names = (f"C{i}" for i in range(columns))
        else:
            column_names = columns

        prev = self.header
        # links every column in a for loop
        for name in column_names:
            if isinstance(name, tuple):
                name, primary = name
            else:
                primary = True
            cell = HeaderCell(name)
            cell.indexes = (-1, self.cols)
            cell.is_first = False
            self.col_list.append(cell)
            if primary:
                prev.R = cell
                cell.L = prev
                prev = cell
            self.cols += 1

        prev.R = self.header
        self.header.L = prev

    def add_sparse_row(self, row: list[int], already_sorted=False):
        """Adds a sparse row to the matrix. The row is in format
        [ind_0, ..., ind_n] where 0 <= ind_i < dl_matrix.ncols.
        If called after end_add is executed, CannotAddRowsError is raised.

        :param row: a sequence of integers indicating the 1s in the row.
        :param already_sorted: True if the row is already sorted,
                               default is False. Use it for performance
                               optimization.
        :raises CannotAddRowsError if end_add was already called.
        """
        if self.col_list is None:
            raise CannotAddRowsError()

        prev = None
        start = None

        if not already_sorted:
            row = sorted(row)

        cell = None
        for ind in row:
            cell = Cell()
            cell.indexes = (self.rows, ind)

            if prev:
                prev.R = cell
                cell.L = prev
            else:
                start = cell

            col = self.col_list[ind]
            # link the cell with the previous one and with the right column
            # cells.
            last = col.U
            last.D = cell
            cell.U = last
            col.U = cell
            cell.D = col
            cell.C = col
            col.size += 1
            prev = cell

        start.L = cell
        cell.R = start
        self.rows += 1

    def end_add(self) -> None:
        """Called when there are no more rows to be inserted. Not strictly
        necessary, but it can save some memory.
        """
        self.col_list = None

    def min_column(self) -> HeaderCell:
        """Returns the column header of the column with the minimum number of 1s.
        :return: A column header.
        :raises: EmptyDLMatrix if the matrix is empty.
        """
        if self.header.R.is_first:
            raise EmptyDLMatrix()

        col_min = self.header.R

        col: HeaderCell
        for col in iterate_cell(self.header, "R"):
            if not col.is_first and col.size < col_min.size:
                col_min = col

        return col_min

    def random_column(self) -> HeaderCell:
        """Returns a random column header. (The matrix header is never returned)
        :return: A column header.
        :raises: EmptyDLMatrix if the matrix is empty.
        """
        col = self.header.R
        if col is self.header:
            raise EmptyDLMatrix()

        n = random.randint(0, self.cols - 1)

        for _ in range(n):
            col = col.R

        if col.is_first:
            col = col.R
        return col

    def __str__(self):
        names = []
        m = np.zeros((self.rows, self.cols), dtype=np.uint8)
        rows, cols = set(), []

        col: HeaderCell
        for col in iterate_cell(self.header, "R"):
            cols.append(col.indexes[1])
            names.append(col.name)

            for cell in iterate_cell(col, "D"):
                ind = cell.indexes
                rows.add(ind[0])
                m[ind] = 1

        m = m[list(rows)][:, cols]
        return "\n".join([", ".join(names), str(m)])

    @staticmethod
    def cover(c: HeaderCell) -> None:
        """Covers the column c by removing the 1s in the column and also all
        the rows connected to them.

        :param c: The column header of the column that has to be covered.

        """
        c.R.L = c.L
        c.L.R = c.R

        for i in iterate_cell(c, "D"):
            for j in iterate_cell(i, "R"):
                j.D.U = j.U
                j.U.D = j.D
                j.C.size -= 1

    @staticmethod
    def uncover(c: HeaderCell) -> None:
        """Uncovers the column c by re-adding the 1s in the column and also all
        the rows connected to them.

        :param c: The column header of the column that has to be uncovered.
        """
        for i in iterate_cell(c, "U"):
            for j in iterate_cell(i, "L"):
                j.C.size += 1
                j.D.U = j.U.D = j

        c.R.L = c.L.R = c


def iterate_cell(cell: Cell, direction: Literal["U", "D", "L", "R"]) -> Iterable[Cell]:
    cur: Cell = getattr(cell, direction)
    while cur is not cell:
        yield cur
        cur = getattr(cur, direction)


# TODO to be completed
class MatrixDisplayer:
    def __init__(self, matrix):
        dic = {}

        for col in iterate_cell(matrix.header, "R"):
            dic[col.indexes] = col

        for col in iterate_cell(matrix.header, "R"):
            first = col.D
            dic[first.indexes] = first
            for cell in iterate_cell(first, "D"):
                if cell is not col:
                    dic[cell.indexes] = cell

        self.dic = dic
        self.rows = matrix.rows
        self.cols = matrix.cols

    def print_matrix(self):
        m = {}

        for i in range(-1, self.rows):
            for j in range(0, self.cols):
                cell = self.dic.get((i, j))
                if cell:
                    if i == -1:
                        m[0, 2 * j] = cell.name
                    else:
                        m[2 * (i + 1), 2 * j] = "X"

        for i in range(-1, self.rows * 2):
            for j in range(0, self.cols * 2):
                print(m.get((i, j), " "), end="")
            print()


if __name__ == "__main__":

    def from_dense(row):
        return [i for i, el in enumerate(row) if el]

    r = [
        from_dense([1, 0, 0, 1, 0, 0, 1]),
        from_dense([1, 0, 0, 1, 0, 0, 0]),
        from_dense([0, 0, 0, 1, 1, 0, 1]),
        from_dense([0, 0, 1, 0, 1, 1, 0]),
        from_dense([0, 1, 1, 0, 0, 1, 1]),
        from_dense([0, 1, 0, 0, 0, 0, 1]),
    ]

    d = DancingLinksMatrix("1234567")

    for row in r:
        d.add_sparse_row(row, already_sorted=True)
    d.end_add()

    p = MatrixDisplayer(d)
    p.print_matrix()

    # print(d.rows)
    # print(d.cols)
    # print(d)

    mc = d.min_column()
    # print(mc)

    d.cover(mc)
    # print(d)

    p.print_matrix()

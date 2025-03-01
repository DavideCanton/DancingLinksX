"""Implementation of Donald Knuth's Dancing Links Sparse Matrix.

It uses a circular doubly linked list.
See http://arxiv.org/abs/cs/0011047.
"""

from __future__ import annotations

import random
from collections.abc import Iterable, Mapping
from typing import Literal, Self

__author__ = "Davide Canton"


class CannotAddRowsError(Exception):
    """Exception raised if no rows can be added to the matrix."""


class EmptyDLMatrix(Exception):
    """Exception raised if the matrix is empty."""


class Cell:
    """Inner cell.

    It stores 4 pointers to neighbors, a pointer to the column header and the indexes associated.
    """

    U: Cell
    D: Cell
    L: Cell
    R: Cell
    C: HeaderCell
    indexes: tuple[int, int]

    __slots__ = ["C", "D", "L", "R", "U", "indexes"]

    def __init__(self) -> None:
        self.U = self.D = self.L = self.R = self

    def __str__(self) -> str:
        return f"Node: {self.indexes}"

    def __repr__(self) -> str:
        return f"Cell[{self.indexes}]"


class HeaderCell(Cell):
    """Column Header cell.

    This is a special cell that stores also a ``name`` and a ``size`` member.
    """

    L: HeaderCell
    R: HeaderCell

    name: str
    size: int
    is_first: bool

    __slots__ = ["is_first", "name", "size"]

    def __init__(self, name: str, index: int) -> None:
        super().__init__()
        self.name = name
        self.indexes = (-1, index)
        self.size = 0
        self.is_first = False

    @classmethod
    def First(cls) -> Self:
        header = cls("<H>", -1)
        header.is_first = True
        return header


class DancingLinksMatrix:
    """Dancing Links sparse matrix implementation.

    It stores a circular doubly linked list of 1s, and another list
    of column headers. Every cell points to its upper, lower, left and right
    neighbors in a circular fashion.
    """

    header: HeaderCell
    rows: int
    cols: int
    col_list: list[HeaderCell]
    done: bool = False

    def __init__(self, columns: int | Iterable[str]) -> None:
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
        self.header = HeaderCell.First()
        self.rows = self.cols = 0
        self.col_list = []
        self._create_column_headers(columns)

    def _create_column_headers(self, columns: int | Iterable[str | tuple[str, bool]]) -> None:
        prev = self.header
        # links every column in a for loop
        for name, primary in _normalize(columns):
            cell = HeaderCell(name, self.cols)
            self.col_list.append(cell)
            if primary:
                prev.R = cell
                cell.L = prev
                prev = cell
            self.cols += 1

        prev.R = self.header
        self.header.L = prev

    def add_sparse_row(self, row: list[int], already_sorted=False) -> None:
        """Adds a sparse row to the matrix.

        The row is in format
        ``[ind_0, ..., ind_n]`` where ``0 <= ind_i < dl_matrix.ncols``.
        If called after end_add is executed, ``CannotAddRowsError`` is raised.

        :param row: a sequence of integers indicating the 1s in the row.
        :param already_sorted: True if the row is already sorted,
                               default is False. Use it for performance
                               optimization.
        :raises CannotAddRowsError if end_add was already called.
        """
        if self.done:
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

        assert cell
        assert start

        start.L = cell
        cell.R = start
        self.rows += 1

    def end_add(self) -> None:
        """Called when there are no more rows to be inserted.

        Not strictly necessary, but it can save some memory.
        """
        self.done = True
        self.col_list.clear()

    def min_column(self) -> HeaderCell:
        """Returns the column header of the column with the minimum number of 1s.

        :return: A column header.
        :raises: EmptyDLMatrix if the matrix is empty.
        """
        if self.header.R.is_first:
            raise EmptyDLMatrix()

        col_min = self.header.R

        for col in iterate_cell(self.header, "R"):
            # R of header cell is a header cell
            assert isinstance(col, HeaderCell)
            if not col.is_first and col.size < col_min.size:
                col_min = col

        return col_min

    def random_column(self) -> HeaderCell:
        """Returns a random column header.

        The matrix header is never returned.

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

    @staticmethod
    def cover(col: HeaderCell) -> None:
        """Covers the column ``col``.

        It is done by removing the 1s in the column and also all
        the rows connected to them.

        :param col: The column header of the column that has to be covered.
        """
        col.R.L = col.L
        col.L.R = col.R

        for i in iterate_cell(col, "D"):
            for j in iterate_cell(i, "R"):
                j.D.U = j.U
                j.U.D = j.D
                j.C.size -= 1

    @staticmethod
    def uncover(col: HeaderCell) -> None:
        """Uncovers the column c.

        It is done by re-adding the 1s in the column and also all
        the rows connected to them.

        :param c: The column header of the column that has to be uncovered.
        """
        for i in iterate_cell(col, "U"):
            for j in iterate_cell(i, "L"):
                j.C.size += 1
                j.D.U = j.U.D = j

        col.R.L = col.L.R = col


def _normalize(
    columns: int | Iterable[str | tuple[str, bool]],
) -> Iterable[tuple[str, bool]]:
    if isinstance(columns, int):
        for i in range(columns):
            yield (f"C{i}", True)
    else:
        for t in columns:
            if isinstance(t, str):
                yield (t, True)
            else:
                yield t


def iterate_cell(cell: Cell, direction: Literal["U", "D", "L", "R"]) -> Iterable[Cell]:
    cur: Cell = getattr(cell, direction)
    while cur is not cell:
        yield cur
        cur = getattr(cur, direction)


def iterate_headers(cell: HeaderCell, direction: Literal["L", "R"]) -> Iterable[HeaderCell]:
    for c in iterate_cell(cell, direction):
        assert isinstance(c, HeaderCell)
        yield c


# TODO to be completed
class MatrixDisplayer:
    cells: Mapping[tuple[int, int], Cell]
    headers: Mapping[int, HeaderCell]

    def __init__(self, matrix: DancingLinksMatrix) -> None:
        cells = {}
        headers = {}

        for col in iterate_headers(matrix.header, "R"):
            headers[col.indexes[1]] = col

        for col in iterate_headers(matrix.header, "R"):
            first = col.D
            cells[first.indexes] = first
            for cell in iterate_cell(first, "D"):
                if cell is not col:
                    cells[cell.indexes] = cell

        self.cells = cells
        self.headers = headers
        self.rows = matrix.rows
        self.cols = matrix.cols

    def print_matrix(self) -> None:
        m = {}

        for i in range(-1, self.rows):
            if i == -1:
                for j in range(0, self.cols):
                    header = self.headers[j]
                    m[0, 2 * j] = header.name
            else:
                for j in range(0, self.cols):
                    if (i, j) in self.cells:
                        m[2 * (i + 1), 2 * j] = "X"

        for i in range(-1, self.rows * 2):
            for j in range(0, self.cols * 2):
                print(m.get((i, j), " "), end="")
            print()

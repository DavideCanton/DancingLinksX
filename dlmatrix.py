__author__ = "Davide Canton"

# /*
# Copyright (c) 2014, Davide Canton
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
# must display the following acknowledgement:
# This product includes software developed by the <organization>.
# 4. Neither the name of the <organization> nor the
# names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# */

#
# Implementation of Donald Knuth's Dancing Links Sparse Matrix
# as a circular doubly linked list. (http://arxiv.org/abs/cs/0011047)
#

import random
import numpy as np


class CannotAddRowsError(Exception):
    pass


class EmptyDLMatrix(Exception):
    pass


class Cell:
    """
    Inner cell, storing 4 pointers to neighbors, a pointer to the column header
    and the indexes associated.
    """
    __slots__ = list("UDLRC") + ["indexes"]

    def __init__(self):
        self.U = self.D = self.L = self.R = self
        self.C = None
        self.indexes = None

    def __str__(self):
        return "Node: {}".format(self.indexes)


class HeaderCell(Cell):
    """
    Column Header cell, a special cell that stores also a name and a size
    member.
    """
    __slots__ = ["size", "name"]

    def __init__(self, name):
        super(HeaderCell, self).__init__()
        self.size = 0
        self.name = name


class DLMatrix:
    """
    Dancing Links sparse matrix implementation.
    It stores a circular doubly linked list of 1s, and another list
    of column headers. Every cell points to its upper, lower, left and right
    neighbors in a circular fashion.
    """

    def __init__(self, columns):
        """
        Creates a DL_Matrix.

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
        self.header = HeaderCell("H")
        self.nrows = self.ncols = 0
        self.col_list = []
        self._create_column_headers(columns)

    def _create_column_headers(self, columns):
        if isinstance(columns, int):
            columns = int(columns)
            column_names = ("C{}".format(i) for i in range(columns))
        else:
            try:
                column_names = iter(columns)
            except TypeError:
                raise TypeError("Argument is not valid")

        prev = self.header
        # links every column in a for loop
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
        """
        Adds a sparse row to the matrix. The row is in format
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

        for ind in row:
            cell = Cell()
            cell.indexes = (self.nrows, ind)

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
        self.nrows += 1

    def end_add(self):
        """
        Called when there are no more rows to be inserted. Not strictly
        necessary, but it can save some memory.
        """
        self.col_list = None

    def min_column(self):
        """
        Returns the column header of the column with the minimum number of 1s.
        :return: A column header.
        :raises: EmptyDLMatrix if the matrix is empty.
        """
        col = self.header.R
        if col is self.header:
            raise EmptyDLMatrix()

        col_min = col

        while col is not self.header:
            if col.size < col_min.size:
                col_min = col
            col = col.R

        return col_min

    def random_column(self):
        """
        Returns a random column header. (The matrix header is never returned)
        :return: A column header.
        :raises: EmptyDLMatrix if the matrix is empty.
        """
        col = self.header.R
        if col is self.header:
            raise EmptyDLMatrix()

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
            names.append(col.name)
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
        """
        Covers the column c by removing the 1s in the column and also all
        the rows connected to them.

        :param c: The column header of the column that has to be covered.

        """
        # print("Cover column", c.name)
        c.R.L = c.L
        c.L.R = c.R
        i = c.D
        while i is not c:
            j = i.R
            while j is not i:
                j.D.U = j.U
                j.U.D = j.D
                j.C.size -= 1
                j = j.R
            i = i.D

    def uncover(self, c):
        """
        Uncovers the column c by readding the 1s in the column and also all
        the rows connected to them.

        :param c: The column header of the column that has to be uncovered.
        """
        # print("Uncover column", c.name)
        i = c.U
        while i is not c:
            j = i.L
            while j is not i:
                j.C.size += 1
                j.D.U = j.U.D = j
                j = j.L
            i = i.U
        c.R.L = c.L.R = c


def main():
    def from_dense(row):
        return [i for i, el in enumerate(row) if el]

    r = [from_dense([1, 0, 0, 1, 0, 0, 1]),
         from_dense([1, 0, 0, 1, 0, 0, 0]),
         from_dense([0, 0, 0, 1, 1, 0, 1]),
         from_dense([0, 0, 1, 0, 1, 1, 0]),
         from_dense([0, 1, 1, 0, 0, 1, 1]),
         from_dense([0, 1, 0, 0, 0, 0, 1])]

    d = DLMatrix("1234567")

    for row in r:
        d.add_sparse_row(row, already_sorted=True)

    print(d.nrows)
    print(d.ncols)
    print(d)

    mc = d.min_column()
    print(mc)

    d.cover(mc)
    print(d)


if __name__ == '__main__':
    main()

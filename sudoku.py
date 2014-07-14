__author__ = 'Davide Canton'

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
# Sudoku Solver using Dancing Links.
#

import itertools as it

import numpy as np

from dlmatrix import DLMatrix
from alg_x import AlgorithmX
from sudoku_board import Sudoku_Board


def column_names():
    # 81, RiCj = j + 9i
    for i, j in it.product(range(1, 10), repeat=2):
        yield "R{}C{}".format(i, j)
    # 81, Ri#v = v + 9i
    for i, j in it.product(range(1, 10), repeat=2):
        yield "R{}#{}".format(i, j)
    # 81, Cj#v = v + 9j
    for i, j in it.product(range(1, 10), repeat=2):
        yield "C{}#{}".format(i, j)
    # 81, Bn#v = v + 9n
    for i, j in it.product(range(1, 10), repeat=2):
        yield "B{}#{}".format(i, j)


def get_square_index(i, j):
    i, j = i // 3, j // 3
    return 3 * i + j


def compute_row(i, j, v):
    i -= 1
    j -= 1
    v -= 1
    i1 = j + 9 * i
    i2 = 81 + v + 9 * i
    i3 = 81 * 2 + v + 9 * j
    i4 = 81 * 3 + v + 9 * get_square_index(i, j)
    return [i1, i2, i3, i4]


class GetFirstSol:
    def __init__(self):
        self.sol = None

    def __call__(self, sol):
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
    def __init__(self):
        self.count = 0

    def __call__(self, _):
        self.count += 1


def main():
    matrix = DLMatrix(column_names())

    # init with known cells, maybe could be loaded from a file!
    known = {(1, 1): 4, (1, 2): 5, (1, 3): 6, (1, 4): 1,
             (1, 5): 2, (1, 6): 8, (1, 7): 9, (1, 8): 3,
             (1, 9): 7, (2, 1): 1, (3, 1): 8, (4, 1): 5,
             (5, 1): 2, (6, 1): 3, (7, 1): 6, (8, 1): 9,
             (9, 1): 7}
    for i, j in it.product(range(1, 10), repeat=2):
        if (i, j) in known:
            row = compute_row(i, j, known[i, j])
            matrix.add_sparse_row(row, already_sorted=True)
        else:
            for v in range(1, 10):
                row = compute_row(i, j, v)
                matrix.add_sparse_row(row, already_sorted=True)

    matrix.end_add()

    sol = GetFirstSol()
    alg = AlgorithmX(matrix, sol)
    alg()

    board = Sudoku_Board(sol.sol)
    print(board)
    print(board.valid())


if __name__ == "__main__":
    main()

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
# N-queens solver using Dancing Links.
#

from dl_matrix import DancingLinksMatrix
from alg_x import AlgorithmX


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

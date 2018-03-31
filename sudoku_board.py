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
# Sudoku Board implementation.
#

import numpy as np
from numpy.lib.stride_tricks import as_strided


class Sudoku_Board:
    def __init__(self, m=None):
        """
        Creates a board. If m is not None, it is copied.
        :param m: a ndarray or a list of lists.
        """
        if m is not None:
            self._board = np.array(m, dtype=np.uint8)
        else:
            self._board = np.zeros((9, 9), dtype=np.uint8)
        self.squares = as_strided(self._board, shape=(3, 3, 3, 3),
                                  strides=(27, 3, 9, 1))

    def all_filled(self):
        """
        Returns True if there are no empty cells.
        :return: True if all the cells are filled.
        """
        return np.count_nonzero(self._board) == 81

    @property
    def board(self):
        """
        Returns the underlying board object.
        """
        return self._board

    def __getitem__(self, key):
        """
        Returns the item at position key.
        :param key: A tuple of 0-based indices.
        :return: An integer between 1 and 9, or 0 if the cell is empty.
        :raises ValueError if the position is invalid.
        """
        if self._valid_position(key):
            return self._board[key]
        else:
            raise ValueError("Invalid position")

    def __setitem__(self, key, value):
        """
        Sets the item at position key.
        :param key: A tuple of 0-based indices.
        :param value: An integer between 1 and 9, or 0 if the cell has to be
        emptied.
        :raises ValueError if the position is invalid.
        """
        if self._valid_position(key) and 0 <= value <= 9:
            self._board[key] = value
        else:
            raise ValueError("Invalid position")

    def _valid_position(self, pos):
        return all(0 <= i <= 8 for i in pos)

    def valid(self):
        """
        Returns True if the board is a valid Sudoku.
        :return: True if the board is a valid Sudoku, False else.
        """
        for i in range(9):
            u = np.unique(self._board[i, :])
            if u.shape[0] < 9 or np.count_nonzero(u) < 9:
                return False
            u = np.unique(self._board[:, i])
            if u.shape[0] < 9 or np.count_nonzero(u) < 9:
                return False
            u = np.unique(self.squares[divmod(i, 3)])
            if u.shape[0] < 9 or np.count_nonzero(u) < 9:
                return False
        return True

    def __str__(self):
        rows = []
        for i in range(9):
            row = []
            for j in range(9):
                el = self._board[i, j]
                if el:
                    row.append(str(el))
                else:
                    row.append(" ")
            rows.append("|".join(row))
        return "\n".join(rows)

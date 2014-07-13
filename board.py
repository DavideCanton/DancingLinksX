__author__ = 'Kami'

import numpy as np
from numpy.lib.stride_tricks import as_strided


class Board:
    def __init__(self, m=None):
        if m is not None:
            self._board = np.array(m, dtype=np.uint8)
        else:
            self._board = np.zeros((9, 9), dtype=np.uint8)
        self.squares = as_strided(self._board, shape=(3, 3, 3, 3),
                                  strides=(27, 3, 9, 1))

    def all_filled(self):
        return np.count_nonzero(self._board) == 81

    @property
    def board(self):
        return self._board

    def __getitem__(self, key):
        if self._valid_position(key):
            return self._board[key]
        else:
            raise ValueError("Invalid position")

    def __setitem__(self, key, value):
        if self._valid_position(key) and 0 <= value <= 9:
            self._board[key] = value
        else:
            raise ValueError("Invalid position")

    def _valid_position(self, pos):
        return all(0 <= i <= 8 for i in pos)

    def valid(self):
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
            rows.append("".join(row))
        return "\n".join(rows)
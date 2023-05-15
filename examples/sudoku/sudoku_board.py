"""Sudoku Board implementation."""

import numpy as np
from numpy.lib.stride_tricks import as_strided

__author__ = "Davide Canton"


class SudokuBoard:
    """Sudoku Board."""

    def __init__(self, m=None):
        """Creates a board.

        If ``m`` is not None, it is copied.

        Args:
            m (np.ndarray | list[list] | None): a ndarray or a list of lists.
        """
        if m is not None:
            self._board = np.array(m, dtype=np.uint8)
        else:
            self._board = np.zeros((9, 9), dtype=np.uint8)
        self.squares = as_strided(self._board, shape=(3, 3, 3, 3), strides=(27, 3, 9, 1))

    @property
    def all_filled(self) -> bool:
        """Returns True if there are no empty cells.

        :return: True if all the cells are filled.
        """
        return np.count_nonzero(self._board) == 81

    @property
    def board(self) -> np.ndarray:
        """Returns the underlying board object."""
        return self._board

    def __getitem__(self, key):
        """Returns the item at position key.

        Args:
            key (tuple[int, ...]): A tuple of 0-based indices.

        Returns:
            int: An integer between 1 and 9, or 0 if the cell is empty.

        Raises:
            ValueError: if the position is invalid.
        """
        if self._valid_position(key):
            return self._board[key]
        else:
            raise ValueError("Invalid position")

    def __setitem__(self, key, value):
        """Sets the item at position key.

        Args:
            key (tuple[int, ...]): A tuple of 0-based indices.
            value (int): An integer between 1 and 9, or 0 if the cell has to be emptied.

        Raises:
            ValueError: if the position is invalid.
        """
        if self._valid_position(key) and 0 <= value <= 9:
            self._board[key] = value
        else:
            raise ValueError("Invalid position")

    def _valid_position(self, pos):
        return all(0 <= i <= 8 for i in pos)

    def valid(self):
        """Returns True if the board is a valid Sudoku.

        Returns:
            bool: True if the board is a valid Sudoku, False else.
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
        """Returns a stringified representation of the board."""
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

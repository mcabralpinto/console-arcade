from tzfe_drawable import Board
from structs import Move2048 as Move, Status

import time
from copy import deepcopy
from pynput.keyboard import Key, KeyCode
from random import random, randint
from typing import Any


class TZFE:
    def __init__(self, arcade: Any) -> None:
        self.arcade: Any = arcade  # arcade instance
        self.SIZE: int = 4  # board size
        self.MOVE: list[KeyCode] = [Key.up, Key.down, Key.left, Key.right]  # move keys

        self.moves: dict[tuple[int, int], Move] = {}  # dict with every moving cell

        self.display = Board(
            dim=(self.SIZE * 5 + 1, self.SIZE * 2 + 3)
        )  # board display

    def start(self) -> None:
        self.score: int = 0  # game score
        self.board: list[list[str]] = [[""] * self.SIZE for _ in range(self.SIZE)]
        self.free_cells: int = self.SIZE * self.SIZE  # number of free cells

    def can_merge(self) -> bool:
        for key in self.MOVE:
            if self.make_moves(deepcopy(self.board), key, True) != self.board:
                return True
        return False

    def fill_board(self, n: int) -> bool:
        self.free_cells -= n
        for _ in range(n):
            i: int
            j: int
            i, j = randint(0, self.SIZE - 1), randint(0, self.SIZE - 1)
            while self.board[i][j] != "":
                i, j = randint(0, self.SIZE - 1), randint(0, self.SIZE - 1)
            self.board[i][j] = "2" if random() > 0.1 else "4"
            if self.free_cells == 0 and not self.can_merge():
                return False
        return True

    def make_moves(
        self, b: list[list[str]], key: KeyCode, can_merge_test: bool = False
    ) -> list[list[str]]:
        shift: tuple[int, int] = ((-1, 0), (1, 0), (0, -1), (0, 1))[
            self.MOVE.index(key)
        ]
        mergeable: list[list[bool]] = [[True] * self.SIZE for _ in range(self.SIZE)]
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                self.moves[(i, j)] = Move(v=b[i][j], s=(0, 0))
        for i in range(
            self.SIZE - 2 if key == Key.down else (1 if key == Key.up else 0),
            -1 if key == Key.down else self.SIZE,
            -1 if key == Key.down else 1,
        ):
            for j in range(
                self.SIZE - 2 if key == Key.right else (1 if key == Key.left else 0),
                -1 if key == Key.right else self.SIZE,
                -1 if key == Key.right else 1,
            ):
                if b[i][j] != "":
                    coors: list[int] = [i, j]
                    value: str = b[i][j]
                    b[i][j] = ""
                    while (
                        coors[0] + shift[0] < self.SIZE
                        and coors[0] + shift[0] >= 0
                        and coors[1] + shift[1] < self.SIZE
                        and coors[1] + shift[1] >= 0
                    ):
                        if b[coors[0] + shift[0]][coors[1] + shift[1]] == "":
                            coors[0] += shift[0]
                            coors[1] += shift[1]
                        elif (
                            b[coors[0] + shift[0]][coors[1] + shift[1]] == value
                            and mergeable[coors[0] + shift[0]][coors[1] + shift[1]]
                        ):
                            coors[0] += shift[0]
                            coors[1] += shift[1]
                            mergeable[coors[0]][coors[1]] = False
                            self.score += 2 * int(value)
                            value = str(2 * int(value))
                            if not can_merge_test:
                                self.free_cells += 1
                            break
                        else:
                            break
                    b[coors[0]][coors[1]] = value
                    self.moves[(i, j)].s = (coors[0] - i, coors[1] - j)
        self.moves = dict[tuple[int, int], Move](
            sorted(
                {a: b for a, b in self.moves.items() if b.v != ""}.items(),
                key=lambda item: max(abs(int(item[1].s[0])), abs(int(item[1].s[1]))),
            )
        )
        return b

    def on_press(self, key: KeyCode) -> None:
        try:
            if key in self.MOVE:
                aux_board: list[list[str]] = self.make_moves(deepcopy(self.board), key)
                if aux_board != self.board:
                    self.board = deepcopy(aux_board)
                    for i in range(5 if key in self.MOVE[0:1] else 4):
                        self.display.draw([self.board, self.score, self.moves, i + 1])
                        time.sleep(0.015)
                    proceed = self.fill_board(1)
                    self.display.draw([self.board, self.score, self.moves, 0])
                    if not proceed:
                        time.sleep(1)
                        self.arcade.transition.draw()
                        self.arcade.status = Status.POST_GAME
                        self.arcade.on_press(Key.up)
            elif key == Key.esc:
                self.arcade.transition.draw()
                self.arcade.status = Status.PRE_GAME
                self.arcade.on_press(Key.up)
        except AttributeError:
            pass

    def run(self):
        self.start()
        self.fill_board(2)
        self.display.draw([self.board, self.score, self.moves, 0])

from game import Game
from tzfe_drawable import Board
from structs import Move2048 as Move, Status

import time
from dataclasses import dataclass, field
from pynput.keyboard import Key, KeyCode
from typing import Any, Optional
from copy import deepcopy
from random import random, randint


@dataclass
class TZFE(Game):
    moves: dict[tuple[int, int], Move] = field(default_factory=dict)  # moving cell info
    SIZE: int = 4  # board size

    def __post_init__(self):
        self.display: Board = Board(dim=(self.SIZE * 5 + 1, self.SIZE * 2 + 3))
        self.KEYS = {"MOVE": [Key.up, Key.down, Key.left, Key.right]}  # key mapping

    def start(self) -> None:
        self.score: int = 0  # game score
        self.board: list[list[str]] = [[""] * self.SIZE for _ in range(self.SIZE)]
        self.free_cells: int = self.SIZE * self.SIZE  # number of free cells
        if self.arcade.status != Status.IN_REPLAY:
            self.arcade.game_info.data["CELLS"] = []

    def can_merge(self) -> bool:
        for key in self.KEYS["MOVE"]:
            if self.make_moves(deepcopy(self.board), key, True) != self.board:
                return True
        return False

    def fill_board(
        self, n: int, cells: list[tuple[int, int, str]] = []
    ) -> tuple[list[tuple[int, int, str]], bool]:
        self.free_cells -= n
        i: int
        j: int
        cells_re: list[tuple[int, int, str]] = []
        for _ in range(n):
            if cells != []:
                i, j, self.board[i][j] = cells.pop()
            else:
                i, j = randint(0, self.SIZE - 1), randint(0, self.SIZE - 1)
                while self.board[i][j] != "":
                    i, j = randint(0, self.SIZE - 1), randint(0, self.SIZE - 1)
                self.board[i][j] = "2" if random() > 0.1 else "4"
                cells_re.append((i, j, self.board[i][j]))
            if self.free_cells == 0 and not self.can_merge():
                return cells_re, False
        return cells_re, True

    def make_moves(
        self, b: list[list[str]], key: KeyCode, can_merge_test: bool = False
    ) -> list[list[str]]:
        shift: tuple[int, int] = ((-1, 0), (1, 0), (0, -1), (0, 1))[
            self.KEYS["MOVE"].index(key)
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

    def on_press(self, key: KeyCode, info: list[Any] = []) -> None:
        c: Optional[tuple[int, int, str]] = info[0] if info != [] else None
        try:
            if key in self.KEYS["MOVE"]:
                aux_board: list[list[str]] = self.make_moves(deepcopy(self.board), key)
                if aux_board != self.board:
                    self.board = deepcopy(aux_board)

                    for i in range(5 if key in self.KEYS["MOVE"][0:1] else 4):
                        if c != None and self.arcade.status != Status.IN_REPLAY:
                            break
                        self.display.draw([self.board, self.score, self.moves, i + 1])
                        time.sleep(0.015)
                    r: bool = self.arcade.status == Status.IN_REPLAY
                    cells, proceed = self.fill_board(1, [c] if r and c != None else [])
                    if r:
                        self.arcade.game_info.keys.append(key)
                        self.arcade.game_info.data["CELLS"] += cells
                    if c == None or r:
                        self.display.draw([self.board, self.score, self.moves, 0])
                    if not proceed:
                        time.sleep(1)
                        self.arcade.game_info.score = self.score
                        self.arcade.game_info.data["CELLS"].reverse()
                        self.arcade.transition.draw()
                        self.arcade.status = Status.POST_GAME
                        self.arcade.on_press(Key.up)
            elif key == Key.esc:
                self.arcade.transition.draw()
                self.arcade.status = Status.PRE_GAME
                self.arcade.on_press(Key.up)
        except AttributeError:
            pass

    def run_replay(self):
        self.board = [[""] * self.SIZE for _ in range(self.SIZE)]
        cells = deepcopy(self.arcade.game_info.data["CELLS"])
        self.fill_board(2, [cells.pop() for _ in range(2)])
        self.display.draw([self.board, self.score, self.moves, 0])
        for key in self.arcade.game_info.keys:
            time.sleep(0.2)
            if self.arcade.status != Status.IN_REPLAY:
                break
            self.on_press(key, [cells.pop()])
        self.arcade.game_info.clear()
        self.arcade.status = Status.PRE_GAME

    def run(self):
        try:
            self.start()
            if self.arcade.status != Status.IN_REPLAY:
                cells, _ = self.fill_board(2, [])
                self.arcade.game_info.data["CELLS"] += cells
                self.display.draw([self.board, self.score, self.moves, 0])
        except KeyboardInterrupt:
            pass

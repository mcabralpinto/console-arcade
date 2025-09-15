from game import Game
from utils import Status, Coordinate
from tzfe.drawable import Board
from tzfe.utils import Move

import time
from dataclasses import dataclass, field
from pynput.keyboard import Key, KeyCode
from typing import Any, Optional
from copy import deepcopy
from random import random, randint


@dataclass
class TZFE(Game):
    moves: dict[Coordinate, Move] = field(default_factory=dict)  # moving cell info
    SIZE: int = 4  # board size

    def __post_init__(self):
        dim = Coordinate(self.SIZE * 5 + 1, self.SIZE * 2 + 3)
        self.display = {"BOARD": Board(dim=dim)}
        self.KEYS = {"MOVE": [Key.up, Key.down, Key.left, Key.right]}  # key mapping
        self.standalone = self.arcade is None
        self.running = True

    def start(self) -> None:
        self.score: int = 0  # game score
        self.board: list[list[str]] = [[""] * self.SIZE for _ in range(self.SIZE)]
        self.free_cells: int = self.SIZE * self.SIZE  # number of free cells
        if not self.standalone and self.arcade.status != Status.IN_REPLAY:
            self.arcade.game_info.data["CELLS"] = []

    def render(self, phase: int = 0) -> None:
        self.display["BOARD"].draw([self.board, self.score, self.moves, phase])

    def can_merge(self) -> bool:
        for key in self.KEYS["MOVE"]:
            if self.make_moves(deepcopy(self.board), key, True) != self.board:
                return True
        return False

    def fill_board(
        self, n: int, cells: list[tuple[int, int, str]] = []
    ) -> tuple[list[tuple[int, int, str]], bool]:
        self.free_cells -= n
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
        self,
        b: list[list[str]],
        key: KeyCode,
        can_merge_test: bool = False,
    ) -> list[list[str]]:
        shift_vector = ((0, -1), (0, 1), (-1, 0), (1, 0))[self.KEYS["MOVE"].index(key)]
        shift = Coordinate(*shift_vector)
        mergeable: list[list[bool]] = [[True] * self.SIZE for _ in range(self.SIZE)]
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                self.moves[Coordinate(j, i)] = Move(
                    value=b[i][j],
                    shift=Coordinate(0, 0),
                )
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
                    coors = Coordinate(j, i)
                    value: str = b[i][j]
                    b[i][j] = ""
                    while (
                        coors.y + shift.y < self.SIZE
                        and coors.y + shift.y >= 0
                        and coors.x + shift.x < self.SIZE
                        and coors.x + shift.x >= 0
                    ):
                        if b[coors.y + shift.y][coors.x + shift.x] == "":
                            coors += shift
                        elif (
                            b[coors.y + shift.y][coors.x + shift.x] == value
                            and mergeable[coors.y + shift.y][coors.x + shift.x]
                        ):
                            coors += shift
                            mergeable[coors.y][coors.x] = False
                            self.score += 2 * int(value)
                            value = str(2 * int(value))
                            if not can_merge_test:
                                self.free_cells += 1
                            break
                        else:
                            break
                    b[coors.y][coors.x] = value
                    self.moves[Coordinate(j, i)].shift = Coordinate(
                        coors.x - j,
                        coors.y - i,
                    )
        self.moves = dict[Coordinate, Move](
            sorted(
                {a: b for a, b in self.moves.items() if b.value != ""}.items(),
                key=lambda item: max(
                    abs(int(item[1].shift.y)), abs(int(item[1].shift.x))
                ),
            )
        )
        return b

    def on_press(self, key: KeyCode, info: list[Any] = []) -> None:
        # new cells to be added to the board (for replays)
        c: Optional[tuple[int, int, str]] = info[0] if info != [] else None
        try:
            if key in self.KEYS["MOVE"]:
                aux_board = self.make_moves(deepcopy(self.board), key)
                if aux_board != self.board:
                    self.board = deepcopy(aux_board)

                    for i in range(4):
                        if (not self.standalone) and (
                            c != None and self.arcade.status != Status.IN_REPLAY
                        ):
                            break
                        self.render(i + 1)
                        time.sleep(0.015)
                    r = (
                        self.arcade.status == Status.IN_REPLAY
                        if not self.standalone
                        else False
                    )
                    cells, proceed = self.fill_board(1, [c] if r and c != None else [])
                    if not self.standalone and c == None:
                        self.arcade.game_info.keys.append(key)
                        self.arcade.game_info.data["CELLS"] += cells
                    self.render(0)
                    if not proceed:
                        time.sleep(1)
                        if not self.standalone:
                            if c == None:
                                self.arcade.game_info.score = self.score
                                self.arcade.game_info.data["CELLS"].reverse()
                            self.arcade.transition.draw()
                            self.arcade.status = (
                                Status.POST_GAME if c == None else Status.PRE_GAME
                            )
                            self.arcade.on_press(Key.up)
                        else:
                            self.running = False

            elif key == Key.esc:
                if not self.standalone:
                    self.arcade.transition.draw()
                    self.arcade.status = Status.PRE_GAME
                    self.arcade.on_press(Key.up)
                else:
                    self.running = False

        except AttributeError:
            pass

    def run_replay(self):
        self.board = [[""] * self.SIZE for _ in range(self.SIZE)]
        cells = deepcopy(self.arcade.game_info.data["CELLS"])
        self.fill_board(2, [cells.pop() for _ in range(2)])
        self.render(0)
        for key in self.arcade.game_info.keys:
            time.sleep(0.05)
            if self.arcade.status != Status.IN_REPLAY:
                break
            self.on_press(key, [cells.pop()])
        self.arcade.game_info.clear()

    def run(self):
        try:
            self.start()
            if not self.standalone:
                replay = self.arcade.status == Status.IN_REPLAY
            else:
                replay = False

            if not replay:
                cells, _ = self.fill_board(2, [])
                if not self.standalone:
                    self.arcade.game_info.data["CELLS"] += cells
                self.render(0)

            if self.standalone:
                from pynput import keyboard
                import os

                def on_key_press(key):
                    self.on_press(key)
                    if not self.running:
                        listener.stop()

                with keyboard.Listener(on_press=on_key_press) as listener:
                    listener.join()

                os.system("cls" if os.name == "nt" else "clear")

        except KeyboardInterrupt:
            pass

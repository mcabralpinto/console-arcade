from structs import Status
from abalone_drawable import Board

from dataclasses import dataclass, field
from copy import copy, deepcopy
from pynput.keyboard import Key, KeyCode
from typing import Any
import time


class Abalone:
    def __init__(self, arcade: Any):
        self.arcade: Any = arcade  # arcade instance

        self.WIDTH: int = 22
        self.HEIGHT: int = 13  # game dimensions
        self.MOVE: tuple[KeyCode, KeyCode, KeyCode, KeyCode] = (
            Key.up,
            Key.down,
            Key.left,
            Key.right,
        )  # movement keys
        self.BOARD_POS: list[list[tuple[int, int]]] = [
            [(i, abs(4 - i) + 2 * j) for j in range(9 - abs(4 - i))] for i in range(9)
        ]  # array with "true" board position coordinates, helps with several operations

        self.display: Board = Board(dim=(self.WIDTH, self.HEIGHT)) # board display

    def start(self, dispo: str = "") -> None:
        self.board: list[list[str]] = [
            ["·" for _ in range(9 - abs(4 - i))] for i in range(9)
        ]
        self.cursor: list[int] = [4, 4]  # cursor position
        self.play_start: list[int] = []  # coors of the starting position of a play
        self.idx_vector: list[list[int]] = []  # indexes of all pieces moved in a play
        self.turn: bool = True  # True if it's the red player's turn, False otherwise
        self.scores: dict[str, int] = {"R": 0, "B": 0}  # scores of both players
        if dispo != "":
            self.fill_board(dispo)

    def get_indexes(
        self, board_pos: list[list[tuple[int, int]]], coors: tuple[int, ...]
    ) -> list[int]:
        for row_idx, row in enumerate(board_pos):
            for col_idx, element in enumerate(row):
                if element == coors:
                    return [row_idx, col_idx]
        return [-1, -1]

    def fill_board(self, type: str) -> None:
        R, B = self.display.paint("■", "RED"), self.display.paint("■", "BLUE")
        positions = ()
        if type == "classic":
            positions = (
                [(0, i, B) for i in range(5)]
                + [(1, i, B) for i in range(6)]
                + [(2, i + 2, B) for i in range(3)]
                + [(6, i + 2, R) for i in range(3)]
                + [(7, i, R) for i in range(6)]
                + [(8, i, R) for i in range(5)]
            )
        elif type == "belgian_daisy":
            positions = (
                [(0, i, B if i < 2 else R) for i in range(5) if i != 2]
                + [(1, i, B if i < 3 else R) for i in range(6)]
                + [(2, i + 1, B if i < 2 else R) for i in range(5) if i != 2]
                + [(6, i + 1, R if i < 2 else B) for i in range(5) if i != 2]
                + [(7, i, R if i < 3 else B) for i in range(6)]
                + [(8, i, R if i < 2 else B) for i in range(5) if i != 2]
            )

        for piece in positions:
            self.board[piece[0]][piece[1]] = piece[2]

    def check_inline_pos(self) -> bool:
        bp, c, p = self.BOARD_POS, self.cursor, self.play_start
        if p[0] == c[0] and abs(p[1] - c[1]) <= 3:
            return True  # horizontal
        if (
            abs(bp[p[0]][p[1]][1] - bp[c[0]][c[1]][1]) == abs(p[0] - c[0])
            and abs(bp[p[0]][p[1]][1] - bp[c[0]][c[1]][1]) <= 3
        ):
            return True  # diagonal
        return False

    def check_inline_count(self, team: bool) -> int:
        b, bp, c, p = self.board, self.BOARD_POS, self.cursor, self.play_start
        R, B = self.display.paint("■", "RED"), self.display.paint("■", "BLUE")
        RC, BC = self.display.paint("▣", "RED"), self.display.paint("▣", "BLUE")
        count = 1

        dynamic, static = list(bp[c[0]][c[1]]), list(bp[p[0]][p[1]])
        shift = [
            0 if dynamic[0] == static[0] else (1 if dynamic[0] < static[0] else -1),
            (
                (1 if dynamic[0] != static[0] else 2)
                if dynamic[1] < static[1]
                else (-1 if dynamic[0] != static[0] else -2)
            ),
        ]
        if not team:
            shift = [-x for x in shift]

        dynamic[0] += shift[0]
        dynamic[1] += shift[1]
        while True:
            if team and dynamic == static:
                break
            idxs = self.get_indexes(self.BOARD_POS, (dynamic[0], dynamic[1]))
            if not team:
                if idxs[0] in list(range(9)):
                    if idxs[1] in list(range(len(b[idxs[0]]))):
                        if b[idxs[0]][idxs[1]] == "·":
                            break
                    else:
                        break
                else:
                    break
            count += 1
            if b[idxs[0]][idxs[1]] not in (
                ([R, RC] if team else [B]) if self.turn else ([B, BC] if team else [R])
            ):
                return 0
            dynamic[0] += shift[0]
            dynamic[1] += shift[1]
        if not team:
            self.idx_vector = [
                self.get_indexes(self.BOARD_POS, (dynamic[0], dynamic[1]))
            ]
        return count

    def check_side(self) -> bool:
        b, bp, c, p = self.board, self.BOARD_POS, self.cursor, self.play_start
        bp_c, bp_p = bp[c[0]][c[1]], bp[p[0]][p[1]]
        bp_c_i, bp_p_i = self.get_indexes(bp, bp_c), self.get_indexes(bp, bp_p)
        BASE_IDX_VECTOR = [bp_c_i, bp_p_i]
        R, B = self.display.paint("■", "RED"), self.display.paint("■", "BLUE")

        if b[bp_c_i[0]][bp_c_i[1]] == "◘":
            self.idx_vector = copy(BASE_IDX_VECTOR)
            valid = True
            # horizontal case
            if abs(bp_p[0] - bp_c[0]) == 1 and abs(bp_p[1] - bp_c[1]) < 6:
                high, low = (
                    list(max(bp_c, bp_p, key=lambda x: x[1])),
                    list(min(bp_c, bp_p, key=lambda x: x[1])),
                )
                h_i, l_i = (
                    self.get_indexes(bp, tuple(high)),
                    self.get_indexes(bp, tuple(low)),
                )
                cbp = bp_c[1] > bp_p[1]
                while high[1] > low[1]:
                    high[1] -= 2
                    low[1] += 2
                    h_i[1] -= 1
                    l_i[1] += 1
                    self.idx_vector += (
                        deepcopy([h_i, l_i]) if cbp else deepcopy([l_i, h_i])
                    )

                    if ((b[h_i[0]][h_i[1]] if cbp else b[l_i[0]][l_i[1]]) != "·") or (
                        (b[l_i[0]][l_i[1]] if cbp else b[h_i[0]][h_i[1]])
                        != (R if self.turn else B)
                    ):
                        valid = False
                        break
                if valid:
                    return True

            self.idx_vector = copy(BASE_IDX_VECTOR)
            valid = False
            offset = False
            shift = [-1 if bp_p[0] > bp_c[0] else 1, -1 if bp_p[1] > bp_c[1] else 1]
            # diagonal case
            for i in range(1, 3):
                if list(bp_c) in [
                    [bp_p[0] + (shift[0] * i), bp_p[1] + (shift[1] * (i + 2))],
                    [bp_p[0] + (shift[0] * (i + 1)), bp_p[1] + (shift[1] * (i - 1))],
                ]:
                    if list(bp_c) == [
                        bp_p[0] + (shift[0] * (i + 1)),
                        bp_p[1] + (shift[1] * (i - 1)),
                    ]:
                        offset = True
                    valid = True
                    break

            if valid:
                bp_c, bp_p = list(bp_c), list(bp_p)
                bp_c_backup, bp_p_backup = copy(bp_c), copy(bp_p)
                bp_c_i, bp_p_i = (
                    self.get_indexes(bp, tuple(bp_c)),
                    self.get_indexes(bp, tuple(bp_p)),
                )
                cbp = bp_c[0] > bp_p[0]
                switched = False
                while (
                    (bp_c[0] > bp_p[0] if cbp else bp_p[0] > bp_c[0]) and offset
                ) or (
                    (bp_c[0] >= bp_p[0] if cbp else bp_p[0] >= bp_c[0]) and not offset
                ):
                    bp_p = [bp_p[0] + shift[0], bp_p[1] + shift[1]]
                    bp_c = [bp_c[0] - shift[0], bp_c[1] - shift[1]]
                    bp_c_i, bp_p_i = (
                        self.get_indexes(bp, tuple(bp_c)),
                        self.get_indexes(bp, tuple(bp_p)),
                    )
                    self.idx_vector += [bp_c_i, bp_p_i]

                    if (b[bp_c_i[0]][bp_c_i[1]] != "·") or (
                        b[bp_p_i[0]][bp_p_i[1]] != (R if self.turn else B)
                    ):
                        if bp_c_backup[1] == bp_p_backup[1] and not switched:
                            switched = True
                            bp_c, bp_p = bp_c_backup, bp_p_backup
                            shift[1] = -shift[1]
                            self.idx_vector = copy(BASE_IDX_VECTOR)
                        else:
                            valid = False
                            break

                if valid:
                    return True

        return False

    def check_move(self) -> int:
        b, c = self.board, self.cursor
        RC, BC = self.display.paint("▣", "RED"), self.display.paint("▣", "BLUE")

        if self.check_inline_pos():
            if (curr_count := self.check_inline_count(True)) > 0:
                if b[c[0]][c[1]] == "◘":
                    return 1
                elif b[c[0]][c[1]] == (BC if self.turn else RC):
                    if curr_count > self.check_inline_count(False):
                        return 2
        if self.check_side():
            return 3
        return -1

    def on_press(self, key: KeyCode) -> None:
        try:
            b, c, p = self.board, self.cursor, self.play_start
            R, B = self.display.paint("■", "RED"), self.display.paint("■", "BLUE")
            RC, BC = self.display.paint("▣", "RED"), self.display.paint("▣", "BLUE")

            if (
                key in list(self.MOVE) + [Key.space]
                and self.arcade.status != Status.IN_REPLAY
            ):
                self.arcade.game_info.keys.append(key)

            if key in self.MOVE:
                if p != [c[0], c[1]]:
                    b[c[0]][c[1]] = {"◘": "·", RC: R, BC: B}[b[c[0]][c[1]]]
                shift = (
                    (-1, 0 if c[0] < 5 else 1),
                    (1, -1 if c[0] in list(range(4, 8)) else 0),
                    (0 if c[1] > 0 or c[0] == 4 else (-1 if c[0] > 4 else 1), -1),
                    (
                        (
                            0
                            if c[1] < len(b[c[0]]) - 1 or c[0] == 4
                            else (-1 if c[0] > 4 else 1)
                        ),
                        1,
                    ),
                )[self.MOVE.index(key)]
                c[0] = min(8, max(0, c[0] + shift[0]))
                c[1] = min(len(b[c[0]]) - 1, max(0, c[1] + shift[1]))
                self.display.draw([self.board, self.cursor, self.scores, self.turn])

            elif key == Key.space:
                if p == []:
                    if b[c[0]][c[1]] == (RC if self.turn else BC):
                        self.play_start = [c[0], c[1]]
                else:
                    if p == [c[0], c[1]]:
                        self.play_start = []
                    else:
                        validity = self.check_move()
                        iv = self.idx_vector
                        if validity == 3:
                            for i in range(0, len(self.idx_vector), 2):
                                b[iv[i][0]][iv[i][1]] = (
                                    (R if i > 1 else RC)
                                    if self.turn
                                    else (B if i > 1 else BC)
                                )
                                b[iv[i + 1][0]][iv[i + 1][1]] = "·"
                            self.play_start = []
                            self.turn = not self.turn
                        if validity == 2:
                            if iv[0][0] in list(range(9)):
                                if iv[0][1] in list(range(len(b[iv[0][0]]))):
                                    b[iv[0][0]][iv[0][1]] = B if self.turn else R
                                else:
                                    self.scores["R" if self.turn else "B"] += 1
                            else:
                                self.scores["R" if self.turn else "B"] += 1
                            validity = 1
                        if validity == 1:
                            b[c[0]][c[1]] = b[p[0]][p[1]]
                            b[p[0]][p[1]] = "·"
                            self.play_start = []
                            self.turn = not self.turn
                        self.idx_vector = []
                if self.scores["B" if self.turn else "R"] < 6:
                    self.display.draw([self.board, self.cursor, self.scores, self.turn])
                else:
                    self.arcade.transition.draw()
                    if self.arcade.status != Status.IN_REPLAY:
                        self.arcade.game_info.score = self.scores
                        self.arcade.status = Status.POST_GAME
                    else:
                        self.arcade.status = Status.PRE_GAME
                    self.arcade.on_press(Key.up)

            elif key == Key.esc:
                self.arcade.transition.draw()
                self.arcade.status = Status.PRE_GAME
                self.arcade.on_press(Key.up)

        except AttributeError:
            pass

    def run_replay(self):
        for key in self.arcade.game_info.keys:
            time.sleep(0.5)
            if self.arcade.status != Status.IN_REPLAY:
                break
            self.on_press(key)
        self.arcade.game_info.clear()
        self.arcade.status = Status.PRE_GAME

    def run(self):
        try:
            self.start("belgian_daisy")
            self.display.draw([self.board, self.cursor, self.scores, self.turn])
        except KeyboardInterrupt:
            pass

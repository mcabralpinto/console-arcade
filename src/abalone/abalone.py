from game import Game
from utils import Coordinate, Status
from abalone.drawable import Board

import time
from dataclasses import dataclass, field
from pynput.keyboard import Key, KeyCode
from copy import copy, deepcopy


@dataclass
class Abalone(Game):
    BOARD_POS: list[list[Coordinate]] = field(
        default_factory=lambda: [
            [Coordinate(abs(4 - i) + 2 * j, i) for j in range(9 - abs(4 - i))]
            for i in range(9)
        ]
    )  # array with "true" board position coordinates, helps with several operations

    def __post_init__(self):
        self.display = {"BOARD": Board(dim=Coordinate(22, 13))}
        self.KEYS = {"MOVE": [Key.up, Key.down, Key.left, Key.right]}  # key mapping
        self.standalone = self.arcade is None
        self.running = True

    def start(self, info: str = "") -> None:
        self.board: list[list[str]] = [
            ["·" for _ in range(9 - abs(4 - i))] for i in range(9)
        ]
        self.cursor: Coordinate = Coordinate(4, 4)  # cursor position
        self.selected: Coordinate = Coordinate(-1, -1)  # currently selected piece
        self.pos_vector: list[Coordinate] = []  # coords of all pieces moved in a play
        self.turn: bool = True  # True if it's the red player's turn, False otherwise
        self.scores: dict[str, int] = {"R": 0, "B": 0}  # scores of both players
        if info != "":
            self.fill_board(info)

    def render(self) -> None:
        self.display["BOARD"].draw([self.board, self.cursor, self.scores, self.turn])

    def real_pos(self, coordinate: Coordinate) -> Coordinate:
        # return Coordinate((coordinate.x - abs(4 - coordinate.y)) // 2, coordinate.y)
        for row_idx, row in enumerate(self.BOARD_POS):
            for col_idx, element in enumerate(row):
                if element == coordinate:
                    return Coordinate(col_idx, row_idx)
        return Coordinate(-1, -1)

    def fill_board(self, type: str) -> None:
        R = self.display["BOARD"].paint("■", "RED")
        B = self.display["BOARD"].paint("■", "BLUE")
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
        bp, c, p = self.BOARD_POS, self.cursor, self.selected
        if p.y == c.y and abs(p.x - c.x) <= 3:
            return True  # horizontal
        if abs(bp[p.y][p.x].x - bp[c.y][c.x].x) == abs(p.y - c.y) <= 3:
            return True  # diagonal
        return False

    def check_inline_count(self, team: bool) -> int:
        b, bp, c, p = self.board, self.BOARD_POS, self.cursor, self.selected
        R = self.display["BOARD"].paint("■", "RED")
        B = self.display["BOARD"].paint("■", "BLUE")
        RC = self.display["BOARD"].paint("▣", "RED")
        BC = self.display["BOARD"].paint("▣", "BLUE")
        count = 1

        dynamic, static = bp[c.y][c.x], bp[p.y][p.x]
        shift = Coordinate(
            (
                (1 if dynamic.y != static.y else 2)
                if dynamic.x < static.x
                else (-1 if dynamic.y != static.y else -2)
            ),
            0 if dynamic.y == static.y else (1 if dynamic.y < static.y else -1),
        )
        if not team:
            shift = Coordinate(-shift.x, -shift.y)

        dynamic += shift
        while True:
            if team and dynamic == static:
                break
            position = self.real_pos(dynamic)
            if not team:
                if position.y in list(range(9)):
                    if position.x in list(range(len(b[position.y]))):
                        if b[position.y][position.x] == "·":
                            break
                    else:
                        break
                else:
                    break
            count += 1
            if b[position.y][position.x] not in (
                ([R, RC] if team else [B]) if self.turn else ([B, BC] if team else [R])
            ):
                return 0
            dynamic += shift
        if not team:
            self.pos_vector = [self.real_pos(dynamic)]
        return count

    def check_side(self) -> bool:
        b, bp, c, p = self.board, self.BOARD_POS, self.cursor, self.selected
        bp_c, bp_p = bp[c.y][c.x], bp[p.y][p.x]
        BASE_POS_VECTOR = [copy(c), copy(p)]
        R = self.display["BOARD"].paint("■", "RED")
        B = self.display["BOARD"].paint("■", "BLUE")

        if b[c.y][c.x] == "◘":
            self.pos_vector = copy(BASE_POS_VECTOR)
            valid = True
            # horizontal case
            if abs(bp_p.y - bp_c.y) == 1 and abs(bp_p.x - bp_c.x) < 6:
                if bp_c.x > bp_p.x:
                    high, low = bp_c, bp_p
                else:
                    high, low = bp_p, bp_c
                rp_high, rp_low = self.real_pos(tuple(high)), self.real_pos(tuple(low))
                cbp = bp_c.x > bp_p.x
                while high.x > low.x:
                    high.x -= 2
                    low.x += 2
                    rp_high.x -= 1
                    rp_low.x += 1
                    self.pos_vector += (
                        deepcopy([rp_high, rp_low])
                        if cbp
                        else deepcopy([rp_low, rp_high])
                    )

                    if (
                        (b[rp_high.y][rp_high.x] if cbp else b[rp_low.y][rp_low.x])
                        != "·"
                    ) or (
                        (b[rp_low.y][rp_low.x] if cbp else b[rp_high.y][rp_high.x])
                        != (R if self.turn else B)
                    ):
                        valid = False
                        break
                if valid:
                    return True

            self.pos_vector = copy(BASE_POS_VECTOR)
            valid = False
            offset = False
            shift = Coordinate(
                -1 if bp_p.x > bp_c.x else 1, -1 if bp_p.y > bp_c.y else 1
            )
            # diagonal case
            for i in range(1, 3):
                if bp_c in [
                    [bp_p.x + (shift.x * i), bp_p.y + (shift.y * (i + 2))],
                    [bp_p.x + (shift.x * (i + 1)), bp_p.y + (shift.y * (i - 1))],
                ]:
                    if bp_c == Coordinate(
                        bp_p.x + (shift.x * (i + 1)),
                        bp_p.y + (shift.y * (i - 1)),
                    ):
                        offset = True
                    valid = True
                    break

            if valid:
                bp_c_original, bp_p_original = copy(bp_c), copy(bp_p)
                rp_c, rp_p = self.real_pos(bp_c), self.real_pos(bp_p)
                cbp = bp_c.y > bp_p.y
                switched = False
                while ((bp_c.y > bp_p.y if cbp else bp_p.y > bp_c.y) and offset) or (
                    (bp_c.y >= bp_p.y if cbp else bp_p.y >= bp_c.y) and not offset
                ):
                    bp_c = Coordinate(bp_c.x - shift.x, bp_c.y - shift.y)
                    bp_p = Coordinate(bp_p.x + shift.x, bp_p.y + shift.y)
                    rp_c, rp_p = self.real_pos(bp_c), self.real_pos(bp_p)
                    self.pos_vector += [rp_c, rp_p]

                    if (b[rp_c.y][rp_c.x] != "·") or (
                        b[rp_p.y][rp_p.x] != (R if self.turn else B)
                    ):
                        if bp_c_original.x == bp_p_original.x and not switched:
                            switched = True
                            bp_c, bp_p = bp_c_original, bp_p_original
                            shift.x = -shift.x
                            self.pos_vector = copy(BASE_POS_VECTOR)
                        else:
                            valid = False
                            break

                if valid:
                    return True

        return False

    def check_move(self) -> int:
        b, c = self.board, self.cursor
        RC = self.display["BOARD"].paint("▣", "RED")
        BC = self.display["BOARD"].paint("▣", "BLUE")

        if self.check_inline_pos():
            if (curr_count := self.check_inline_count(True)) > 0:
                if b[c.y][c.x] == "◘":
                    return 1
                elif b[c.y][c.x] == (BC if self.turn else RC):
                    if curr_count > self.check_inline_count(False):
                        return 2
        if self.check_side():
            return 3
        return -1

    def on_press(self, key: KeyCode) -> None:
        try:
            b, c, p = self.board, self.cursor, self.selected
            R = self.display["BOARD"].paint("■", "RED")
            B = self.display["BOARD"].paint("■", "BLUE")
            RC = self.display["BOARD"].paint("▣", "RED")
            BC = self.display["BOARD"].paint("▣", "BLUE")

            if (not self.standalone) and (
                key in list(self.KEYS["MOVE"]) + [Key.space]
                and self.arcade.status != Status.IN_REPLAY
            ):
                self.arcade.game_info.keys.append(key)

            if key in self.KEYS["MOVE"]:
                if p != c:
                    b[c.y][c.x] = {"◘": "·", RC: R, BC: B}[b[c.y][c.x]]
                shift = Coordinate(*(
                    (0 if c.y < 5 else 1, -1),
                    (-1 if c.y in list(range(4, 8)) else 0, 1),
                    (-1, 0 if c.x > 0 or c.y == 4 else (-1 if c.y > 4 else 1)),
                    (
                        1,
                        (
                            0
                            if c.x < len(b[c.y]) - 1 or c.y == 4
                            else (-1 if c.y > 4 else 1)
                        ),
                    ),
                )[self.KEYS["MOVE"].index(key)])
                c.y = min(8, max(0, c.y + shift.y))
                c.x = min(len(b[c.y]) - 1, max(0, c.x + shift.x))
                self.render()

            elif key == Key.space:
                if p == Coordinate(-1, -1):
                    if b[c.y][c.x] == (RC if self.turn else BC):
                        self.selected = Coordinate(c.x, c.y)
                else:
                    if p == c:
                        self.selected = Coordinate(-1, -1)
                    else:
                        validity = self.check_move()
                        iv = self.pos_vector
                        if validity == 3:
                            for i in range(0, len(self.pos_vector), 2):
                                b[iv[i].y][iv[i].x] = (
                                    (R if i > 1 else RC)
                                    if self.turn
                                    else (B if i > 1 else BC)
                                )
                                b[iv[i + 1].y][iv[i + 1].x] = "·"
                            self.selected = Coordinate(-1, -1)
                            self.turn = not self.turn
                        if validity == 2:
                            if iv[0].y in list(range(9)):
                                if iv[0].x in list(range(len(b[iv[0].y]))):
                                    b[iv[0].y][iv[0].x] = B if self.turn else R
                                else:
                                    self.scores["R" if self.turn else "B"] += 1
                            else:
                                self.scores["R" if self.turn else "B"] += 1
                            validity = 1
                        if validity == 1:
                            b[c.y][c.x] = b[p.y][p.x]
                            b[p.y][p.x] = "·"
                            self.selected = Coordinate(-1, -1)
                            self.turn = not self.turn
                        self.pos_vector = []
                self.render()
                if self.scores["B" if self.turn else "R"] == 6:
                    if not self.standalone:
                        self.arcade.transition.draw()
                        if self.arcade.status != Status.IN_REPLAY:
                            self.arcade.game_info.score = self.scores
                            self.arcade.status = Status.POST_GAME
                        else:
                            self.arcade.status = Status.PRE_GAME
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
            self.render()

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

# fix movement

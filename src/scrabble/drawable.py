from drawable import Drawable
from utils import Coordinate, load_data
from scrabble.utils import Tile

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Board(Drawable):
    board: list[list[str]] = field(default_factory=list)
    cursor: Coordinate = field(default_factory=lambda: Coordinate(0, 0))
    scores: dict[int, int] = field(default_factory=dict)
    tiles: dict[int, dict[str, list[Tile]]] = field(default_factory=dict)
    new_words: list[str] = field(default_factory=list)
    turn: int = field(default_factory=int)
    direction: bool = field(default_factory=bool)
    exchange: bool = field(default_factory=bool)
    play_score: int = field(default_factory=int)
    tiles_left: int = field(default_factory=int)

    def update(self, values: list[Any]) -> None:
        (
            self.board,
            self.cursor,
            self.scores,
            self.tiles,
            self.new_words,
            self.turn,
            self.direction,
            self.exchange,
            self.play_score,
            self.tiles_left,
        ) = values

    def get_display_char(self, row: int, col: int) -> str:
        # get the character to display at a position
        tile: Tile = self.board[row][col]
        DATA = load_data("games\\scrabble")

        if self.cursor == (col, row):
            return DATA["CURSOR"][0 if self.direction else 1]
        elif tile is not None:
            if tile.locked:
                color = "B_YELLOW" if tile.value == 0 else "YELLOW"
                return self.paint(tile.letter, color)
            else:
                return tile.letter
        else:
            return DATA["BOARD"][row][col]

    # draws the scrabble board
    def content(self, values: list[Any]) -> None:
        self.update(values)
        S: dict[bool, int] = self.scores
        T: dict[bool, list[Tile]] = self.tiles
        SIZE: int = (self.dim.x - 1) // 4
        turn = self.turn % 2 == 1

        # board
        display: list[str] = []
        display.append(f"┌{'───┬' * (SIZE - 1)}───┐")
        for i in range(SIZE):
            row: str = "│"
            for j in range(SIZE):
                row += f" {self.get_display_char(i, j)} │"
            display.append(row)
            if i < len(self.board) - 1:
                display.append(f"├{'───┼' * (SIZE - 1)}───┤")
            else:
                display.append(f"└{'───┴' * (SIZE - 1)}───┘")

        # hands / scores
        side_space = 2
        middle_len = 23
        side_len = (self.dim.x - 2 * side_space - middle_len) // 2
        side = f"{' ' * side_space}"
        top = f"┌{'─' * 15}┐"
        left_top = self.paint(top, "GREEN" if self.turn % 2 == 1 else "")
        right_top = self.paint(top, "GREEN" if self.turn % 2 == 0 else "")
        bottom = f"└{'─' * 15}┘"
        left_bottom = self.paint(bottom, "GREEN" if self.turn % 2 == 1 else "")
        right_bottom = self.paint(bottom, "GREEN" if self.turn % 2 == 0 else "")
        middle = " " * (self.dim.x - 2 * side_space - 34)

        left_hand = " ".join(T[1]["HAND"][i].letter for i in range(len(T[1]["HAND"])))
        right_hand = " ".join(T[0]["HAND"][i].letter for i in range(len(T[0]["HAND"])))

        left = f"│ {' ' * (13 - len(left_hand))}{left_hand} │"
        if turn:
            left = f"{self.paint(self.move(-2, 0) + '▶ ' + left, 'GREEN')}"
        right = f"│ {right_hand}{' ' * (13 - len(right_hand))} │"
        if not turn:
            right = f"{self.paint(right + ' ◀', 'GREEN')}"
        score = f"{S[1]} - {S[0]}"
        play_score = f"({self.play_score})"
        play_score_offset = " " * len(play_score)
        if turn:
            score = f"{play_score} {score} {play_score_offset}".center(middle_len)
        else:
            score = f"{play_score_offset} {score} {play_score}".center(middle_len)
        left = left.ljust(side_len)
        right = right.rjust(side_len)

        display.append(f"{side}{left_top}{middle}{right_top}{side}")
        display.append(f"{side}{left}{score}{right}{side if turn else ''}")
        display.append(f"{side}{left_bottom}{middle}{right_bottom}{side}")
        display.append(f"{' ' * self.dim.x}")

        # legends
        action1 = "Play" if len(T[turn]["PLAY"]) > 1 else "Pass"
        if self.exchange:
            legend_str = "   ".join(
                [
                    "[1] " + self.paint(action1, "B_BLACK"),
                    "[2] " + self.paint("Exchange", "GREEN"),
                    "[3] " + self.paint("Challenge", "B_BLACK"),
                    "[4] Switch to " + ("↓" if self.direction else "→"),
                ]
            )
        else:
            legend_str = "   ".join(
                [
                    "[1] "
                    + self.paint(action1, "GREEN" if len(T[turn]["PLAY"]) > 1 else ""),
                    "[2] "
                    + self.paint("Exchange", "B_BLACK" if T[turn]["PLAY"] else ""),
                    "[3] "
                    + self.paint(
                        "Challenge",
                        "B_BLACK" if (T[turn]["PLAY"] or not self.new_words) else "",
                    ),
                    "[4] Switch to " + ("↓" if self.direction else "→"),
                ]
            )
        padding = (self.dim.x - len(self.strip_ansi(legend_str))) // 2
        turn_str = f"Turn {self.turn} ({self.tiles_left} tiles remaining)"

        display.append(f"{' ' * padding}{legend_str}{' ' * padding}")
        display.append(f"{' ' * self.dim.x}")
        display.append(turn_str.center(self.dim.x))
        # display.append(str(self.new_words).center(self.dim.x))
        # display.append(str(self.tiles[0]["PLAY"]).center(self.dim.x))
        # display.append(str(self.tiles[1]["PLAY"]).center(self.dim.x))

        for row in display:
            print(row + self.move(-self.dim.x, 1), end="", flush=True)


# line outline
# letter same color as positions
# hide opponent tiles
# add help page?

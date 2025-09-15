from drawable import Drawable
from structs import Move2048 as Move, Coordinate

from dataclasses import dataclass, field
from typing import Any, Generator


@dataclass
class Board(Drawable):
    board: list[list[str]] = field(default_factory=list)
    score: int = field(default_factory=int)
    moves: dict[Coordinate, Move] = field(default_factory=dict)
    phase: int = field(default_factory=int)

    def update(self, values: list[Any]) -> None:
        self.board, self.score, self.moves, self.phase = values

    # draws the abalone board
    def content(self, values: list[Any]) -> None:
        self.update(values)
        SIZE: int = (self.dim.x - 1) // 5
        DATA: dict[str, dict[str, str]] = self.load_data("games\\2048")

        board_str: list[str] = []
        board_str.append(f"┌{'────┬' * (SIZE - 1)}────┐")
        for i in range(SIZE):
            row: str = "│"
            for _ in range(SIZE):
                row += "    │"
            board_str.append(row)
            if i < len(self.board) - 1:
                board_str.append(f"├{'────┼' * (SIZE - 1)}────┤")
            else:
                board_str.append(f"└{'────┴' * (SIZE - 1)}────┘")

        if self.phase == 0:
            iterable: Generator[Coordinate] = (
                Coordinate(j, i)
                for i in range(SIZE)
                for j in range(SIZE)
                if self.board[i][j] != ""
            )
        else:
            iterable: Generator[Coordinate] = (k for k in tuple(self.moves.keys()))

        for coors in iterable:
            if self.phase != 0 and coors not in self.moves:
                continue
            shift = Coordinate(0, 0) if self.phase == 0 else self.moves[coors].shift
            value = (
                self.board[coors.y + shift.y][coors.x + shift.x]
                if self.phase == 0
                else self.moves[coors].value
            )
            real_phase = (self.phase + 4) % 5
            row_idx = int(2 * (coors.y + (real_phase / 5 * shift.y)))
            col_idx = int(5 * (coors.x + (((1 + real_phase) / 5) * shift.x)))

            box = (
                DATA["TL"][board_str[row_idx][col_idx]]
                + "".join(
                    [DATA["TC"][board_str[row_idx][col_idx + i + 1]] for i in range(4)]
                )
                + DATA["TR"][board_str[row_idx][col_idx + 5]],
                DATA["CL"][board_str[row_idx + 1][col_idx]]
                + f"{' ' * (4 - len(value))}{value}"
                + DATA["CR"][board_str[row_idx + 1][col_idx + 5]],
                DATA["BL"][board_str[row_idx + 2][col_idx]]
                + "".join(
                    [
                        DATA["BC"][board_str[row_idx + 2][col_idx + i + 1]]
                        for i in range(4)
                    ]
                )
                + DATA["BR"][board_str[row_idx + 2][col_idx + 5]],
            )
            for k in range(3):
                row_list = list(board_str[row_idx + k])
                for l in range(6):
                    row_list[col_idx + l] = box[k][l]
                board_str[row_idx + k] = "".join(row_list)

        for row in board_str:
            print(row + self.move(-self.dim.x, 1), end="", flush=True)

        print(
            self.move(0, 1)
            + "Score:"
            + (" " * (self.dim.x - 6 - len(str(self.score))))
            + str(self.score),
            end="",
            flush=True,
        )

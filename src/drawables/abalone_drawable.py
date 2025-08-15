from drawables.drawable import Drawable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Board(Drawable):
    board: list[list[str]] = field(default_factory=list)
    cursor: list[int] = field(default_factory=list)
    scores: dict[str, int] = field(default_factory=dict)
    turn: bool = field(default_factory=bool)

    def update(self, values: list[Any]) -> None:
        self.board, self.cursor, self.scores, self.turn = values

    # draws the abalone board
    def content(self, values: list[Any]) -> None:
        self.update(values)
        b, c, s = self.board, self.cursor, self.scores
        W = self.dim[0]
        R, B = self.paint("■", "RED"), self.paint("■", "BLUE")
        RC, BC = self.paint("▣", "RED"), self.paint("▣", "BLUE")
        RE, BE = self.paint("□", "RED"), self.paint("□", "BLUE")
        RA, BA = self.paint("◀", "RED"), self.paint("▶", "BLUE")

        if b[c[0]][c[1]] in ["·", R, B]:
            b[c[0]][c[1]] = {"·": "◘", R: RC, B: BC}[b[c[0]][c[1]]]

        board_str = ""
        for i in range(9):
            board_str += (
                " " * max(0, 9 - len(b[i]))
                + ("▟▛" if i < 4 else ("▜▙" if i > 4 else "▐█"))
                + f" {' '.join(b[i])} "
                + ("▜▙" if i < 4 else ("▟▛" if i > 4 else "█▌"))
                + " " * max(0, 9 - len(b[i]))
                + self.move(-W - 1, 1)
            )

        print(
            # board
            f"{' ' * 5}🬵{'🬹' * 11}🬱{' ' * 5}{self.move(-W - 1, 1)}"
            + board_str
            + f"{' ' * 5}🬊{'🬎' * 11}🬆{' ' * 5}{self.move(-W - 1, 2)}"
            # scores
            + f"    {R * s['R']}{RE * (6 - s['R'])}"
            + f" {RA if self.turn else BA} "
            + f"{B * s['B']}{BE * (6 - s['B'])}    ",
            end="",
            flush=True,
        )

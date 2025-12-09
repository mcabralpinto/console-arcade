from drawable import Drawable
from utils import Coordinate
from carcassonne.utils import (
    Tile as CarcTile,
    # StructureType,
    Structure,
    # Field,
    # Road,
    # RoadBlock,
    # City,
    # Cloister,
    Player,
    Meeple,
)

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class Tile(Drawable):
    tile: CarcTile = field(default_factory=lambda: CarcTile())
    # color_map: ClassVar[dict[type[Structure], tuple[str, str]]] = {
    #     Field: ("B_GREEN", "GREEN"),
    #     Road: ("WHITE", "B_BLACK"),
    #     RoadBlock: ("WHITE", "B_BLACK"),
    #     City: ("B_YELLOW", "YELLOW"),
    #     Cloister: ("B_RED", "RED"),
    # }
    # color_map: ClassVar[dict[type[Structure], tuple[str, str]]] = {
    #     StructureType.FIELD: ("B_GREEN", "GREEN"),
    #     StructureType.ROAD: ("WHITE", "B_BLACK"),
    #     StructureType.ROADBLOCK: ("WHITE", "B_BLACK"),
    #     StructureType.CITY: ("B_YELLOW", "YELLOW"),
    #     StructureType.SHIELD: ("B_CYAN", "CYAN"),
    #     StructureType.CLOISTER: ("B_RED", "RED"),
    # }
    color_map: ClassVar[dict[type[Structure], tuple[str, str]]] = {
        "FIELD": ("B_GREEN", "GREEN"),
        "ROAD": ("WHITE", "B_BLACK"),
        "CITY": ("B_YELLOW", "YELLOW"),
        "SHIELD": ("B_YELLOW", "YELLOW"),
        "CLOISTER": ("B_RED", "RED"),
    }

    def update(self, tile: CarcTile) -> None:
        self.tile = tile if tile else CarcTile()

    def content(self, values: list[CarcTile]) -> None:
        self.update(values)
        if self.tile.structures:
            for i in range(0, 6, 2):  # go through 0, 2, 4
                for j in range(6):
                    top = self.tile.structures[i][j]
                    bottom = self.tile.structures[i + 1][j]
                    if bottom.type == top.type == "SHIELD":
                        color = ("B_CYAN", "CYAN")[self.tile.locked]
                        bg_color = self.color_map["CITY"][self.tile.locked]
                        print(Drawable.paint("▾", color, bg_color), end="", flush=True)
                    else:
                        meeple = self.tile.meeple
                        if meeple and meeple.position == (j, i):
                            color = meeple.color
                        else:
                            color = self.color_map[top.type][self.tile.locked]
                        if meeple and meeple.position == (j, i + 1):
                            bg_color = meeple.color
                        else:
                            bg_color = self.color_map[bottom.type][self.tile.locked]
                        print(Drawable.paint("▀", color, bg_color), end="", flush=True)
                if i in [0, 2]:
                    print(Drawable.move(-6, 1), end="", flush=True)
            print(Drawable.move(0, -2), end="", flush=True)
        else:
            print(
                f"      {Drawable.move(-6, 1)}" * 2,
                f"     {Drawable.move(0, -2)}",
                end="",
                flush=True,
            )


@dataclass
class Board(Drawable):
    tile_display: Tile = field(default_factory=lambda: Tile(dim=Coordinate(6, 3)))
    board: dict[Coordinate, CarcTile] = field(default_factory=dict)
    shift: Coordinate = field(default_factory=lambda: Coordinate(0, 0))

    def update(self, values: list[Any]) -> None:
        (self.board, self.shift) = values

    # draws the scrabble board
    def content(self, values: list[Any]) -> None:
        self.update(values)

        x_range = range(
            -(self.dim.x // 12) + self.shift.x,
            (self.dim.x // 12) + 1 + self.shift.x,
        )
        y_range = range(
            -(self.dim.y // 6) + self.shift.y,
            (self.dim.y // 6) + 1 + self.shift.y,
        )

        # print(
        #     f"╭{'─' * (self.dim.x - 2)}╮{self.move(-self.dim.x, 3)}│",
        #     end="",
        #     flush=True,
        # )
        for y in y_range:
            for x in x_range:
                if (x, y) in self.board:
                    self.tile_display.content(self.board[(x, y)])
                else:
                    self.tile_display.content([])
            print(f"{self.move(-self.dim.x, 3)}", end="", flush=True)
        # print(
        #     f"{self.move(-self.dim.x, 3)}╰{'─' * (self.dim.x - 2)}╯",
        #     end="",
        #     flush=True,
        # )


@dataclass
class UI(Drawable):
    players: list[Player] = field(default_factory=list)

    def update(self, values: list[Any]) -> None:
        (self.players,) = values

    # draws the scrabble board
    def content(self, values: list[Any]) -> None:
        self.update(values)

        display = []
        row = ""
        for i, player in enumerate(self.players):
            row += self.paint(f"Player {i + 1}".center(15), color=player.color)
            if i < len(self.players) - 1:
                row += " "
        display.append(row)
        row = ""
        for i, player in enumerate(self.players):
            row += f"Meeples: {player.meeples}".center(15)
            if i < len(self.players) - 1:
                row += " "
        display.append(row)
        row = ""
        for i, player in enumerate(self.players):
            row += f"Score: {player.score}".center(15)
            if i < len(self.players) - 1:
                row += " "
        display.append(row)

        for row in display:
            print(row + self.move(-self.dim.x, 1), end="", flush=True)

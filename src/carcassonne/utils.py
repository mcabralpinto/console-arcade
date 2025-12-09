from dataclasses import dataclass, field
from abc import ABC
from typing import ClassVar, Iterator
from pynput.keyboard import Key, KeyCode

from enum import Enum

from utils import Coordinate


@dataclass
class Player:
    color: str
    meeples: int = 7
    score: int = 0
    tile: "Tile" = None


@dataclass
class Meeple:
    tile: "Tile"
    color: str
    position: Coordinate
    structure: "Structure"

    def move(self, key: KeyCode):
        new_position = self.position + {
            Key.left: (-1, 0),
            Key.right: (1, 0),
            Key.up: (0, -1),
            Key.down: (0, 1),
        }.get(key)

        new_position.x = max(0, min(5, new_position.x))
        new_position.y = max(0, min(5, new_position.y))
        if not (
            self.tile.structures[new_position.y][new_position.x].type == "SHIELD"
            and any(
                self.tile.structures[neighbor.y][neighbor.x].type == "SHIELD"
                for neighbor in new_position.neighbors(horizontal=False)
            )
        ):
            self.position = new_position
            self.structure = self.tile.structures[new_position.y][new_position.x]


@dataclass
class Structure(ABC):
    tile: "Tile"
    type: str

    def same_type(self, other: "Structure"):
        return self.type == other.type or all(
            x in ("CITY", "SHIELD") for x in (self.type, other.type)
        )


class TileParts(Enum):
    UP = Coordinate(2, 0)
    DOWN = Coordinate(2, 5)
    LEFT = Coordinate(0, 2)
    RIGHT = Coordinate(5, 2)


@dataclass
class Tile:
    structures: list[list[Structure]] = field(default_factory=list)
    position: Coordinate = field(default_factory=lambda: Coordinate(0, 0))
    locked: bool = False
    meeple: Meeple = None
    type_map: ClassVar[dict[type[Structure], tuple[str, str]]] = {
        "F": "FIELD",
        "R": "ROAD",
        "C": "CITY",
        "S": "SHIELD",
        "A": "CLOISTER",
    }
    edge_direction_map: ClassVar[dict[TileParts, Coordinate]] = {
        TileParts.UP: Coordinate(0, -1),
        TileParts.DOWN: Coordinate(0, 1),
        TileParts.LEFT: Coordinate(-1, 0),
        TileParts.RIGHT: Coordinate(1, 0),
    }

    @classmethod
    def init(
        cls,
        raw_structures: list[str],
        position: Coordinate,
    ):
        self = cls(structures=(structures := []), position=position, locked=False)

        for row in raw_structures:
            structure_row = []
            for structure in row:
                structure_row.append(Structure(self, type=self.type_map[structure]))
            structures.append(structure_row)

        return self

    def rotate(self):
        # rotate the board
        new_structures = []
        for i in range(6):
            structure_row = []
            for j in range(6):
                structure = self.structures[5 - j][i]
                structure_row.append(structure)
            new_structures.append(structure_row)
        self.structures = new_structures

        # fix road errors
        for i in range(2):
            for j in range(6):
                if i == 0:
                    a = self.structures[2][j]
                    b = self.structures[3][j]
                    c = self.structures[4][j]
                else:
                    a = self.structures[j][2]
                    b = self.structures[j][3]
                    c = self.structures[j][4]
                if b.type == "ROAD":
                    if a.type == "FIELD":
                        if c.type != "ROAD":
                            b.type = a.type
                        a.type = "ROAD"
                    elif a.type == "ROAD" and c.type == "FIELD":
                        b.type = "FIELD"
                elif a.type == "ROAD" and c.type == "ROAD":
                    b.type = "ROAD"

        count = 0
        for k in Coordinate(2, 2).neighbors():
            count += self.structures[k.y][k.x].type == "ROAD"
        if count > 2:
            self.structures[2][2].type = "FIELD"

    def fits(self, other: "Tile") -> bool:
        # calculate difference in position between the two tiles
        shift = self.position - other.position

        # get the absolute position of the two edge tiles for self and other
        self_idxs, other_idxs = {
            (-1, 0): ((17, 23), (12, 18)),
            (1, 0): ((12, 18), (17, 23)),
            (0, -1): ((32, 33), (2, 3)),
            (0, 1): ((2, 3), (32, 33)),
        }[shift]

        # get main edge structure (self)
        self_structure = self.structures[self_idxs[0] // 6][self_idxs[0] % 6]
        if self_structure.type == "FIELD":
            self_structure = self.structures[self_idxs[1] // 6][self_idxs[1] % 6]

        # get main edge structure (other)
        other_structure = other.structures[other_idxs[0] // 6][other_idxs[0] % 6]
        if other_structure.type == "FIELD":
            other_structure = other.structures[other_idxs[1] // 6][other_idxs[1] % 6]

        return self_structure.type == other_structure.type

    def get_edges(self) -> Iterator["TileEdge"]:
        for edge in [TileParts.UP, TileParts.DOWN, TileParts.LEFT, TileParts.RIGHT]:
            yield TileEdge(
                type=self.structures[edge.value.y][edge.value.x].type,
                position=self.position,
                direction=self.edge_direction_map[edge],
            )

    def get_center_type(self):
        if self.structures[2][2].type == "FIELD":
            return self.structures[3][3].type
        return self.structures[2][2].type


@dataclass
class TileEdge:
    type: str
    position: Coordinate
    direction: Coordinate

    def fits(self, other: "TileEdge") -> bool:
        return (
            self.type == other.type
            and self.direction == -other.direction
            and self.position == other.position + other.direction
        )


@dataclass
class StructureSet:
    type: str
    tiles: list[Tile]
    loose_edges: list[TileEdge]

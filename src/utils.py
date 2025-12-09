from enum import Enum
from dataclasses import dataclass, field
import json
import os
from typing import Any, Union, Iterator
from pynput.keyboard import Key, KeyCode


class Status(Enum):
    PRE_GAME = 0
    POST_GAME = 1
    IN_GAME = 2
    IN_REPLAY = 3


@dataclass
class GameInfo:
    keys: list[KeyCode] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    score: Union[int, dict[str, int]] = field(default_factory=int)

    # clears the keys and data
    def clear(self) -> None:
        self.keys = []
        self.data = {}

    # converts a key array's elements from string to pynput.keyboard.Key
    def str_to_key(self, keys: list[str]) -> list[KeyCode]:
        key_mapping = {
            "space": Key.space,
            "up": Key.up,
            "down": Key.down,
            "right": Key.right,
            "left": Key.left,
        }
        return [key_mapping[key] for key in keys]

    # converts a key array's elements from pynput.keyboard.Key to string
    def key_to_str(self, keys: list[KeyCode]) -> list[str]:
        return [str(key).replace("Key.", "") for key in keys]

    # converts the GameInfo object to a dictionary with string values
    def data_to_str(self) -> dict[str, Any]:
        return {"KEYS": self.key_to_str(self.keys), "DATA": self.data}

    # converts a dictionary with string values to a GameInfo object
    def str_to_data(self, data: dict[str, Any]) -> None:
        self.keys = self.str_to_key(data["KEYS"])
        self.data = data["DATA"]


@dataclass
class Coordinate:
    x: int
    y: int

    def __iter__(self):
        yield self.x
        yield self.y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other) -> bool:
        if isinstance(other, Coordinate):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, (tuple, list)) and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        return False

    def __add__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(self.x + other.x, self.y + other.y)
        elif isinstance(other, (tuple, list)) and len(other) == 2:
            return Coordinate(self.x + other[0], self.y + other[1])
        raise TypeError(f"Cannot add Coordinate and {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(self.x - other.x, self.y - other.y)
        elif isinstance(other, (tuple, list)) and len(other) == 2:
            return Coordinate(self.x - other[0], self.y - other[1])
        raise TypeError(f"Cannot subtract Coordinate and {type(other)}")
    
    def __mul__(self, a: int):
        if isinstance(a, (int, float)):
            return Coordinate(self.x * a, self.y * a)
        raise TypeError(f"Cannot multiply Coordinate and {type(a)}")
    
    def __div__(self, a: int):
        if isinstance(a, (int, float)):
            return Coordinate(self.x / a, self.y / a)
        raise TypeError(f"Cannot multiply Coordinate and {type(a)}")
    
    def __neg__(self):
        return Coordinate(-self.x, -self.y)

    def adjacent(self, other: "Coordinate") -> bool:
        return (self.x == other.x and abs(self.y - other.y) == 1) or (
            self.y == other.y and abs(self.x - other.x) == 1
        )

    def neighbors(
        self,
        vertical=True,
        horizontal=True,
        diagonal=False,
    ) -> Iterator["Coordinate"]:
        # iterate over neighboring coordinates
        if horizontal:
            yield Coordinate(self.x - 1, self.y)
            yield Coordinate(self.x + 1, self.y)
        if vertical:
            yield Coordinate(self.x, self.y - 1)
            yield Coordinate(self.x, self.y + 1)
        if diagonal:
            yield Coordinate(self.x - 1, self.y - 1)
            yield Coordinate(self.x - 1, self.y + 1)
            yield Coordinate(self.x + 1, self.y - 1)
            yield Coordinate(self.x + 1, self.y + 1)

    def in_bounds(self, bound1: "Coordinate", bound2: "Coordinate" = None) -> bool:
        # determine if a point is inside the given bounds
        if bound2 is None:
            return 0 <= self.x <= bound1.x and 0 <= self.y <= bound1.y
        else:
            UB = Coordinate(max(bound1.x, bound2.x), max(bound1.y, bound2.y))
            LB = Coordinate(min(bound1.x, bound2.x), min(bound1.y, bound2.y))
            return LB.x <= self.x <= UB.x and LB.y <= self.y <= UB.y

    def correct(self, bound1: "Coordinate", bound2: "Coordinate" = None) -> None:
        if bound2 is None:
            bound2 = Coordinate(0, 0)

        # set bounds
        UB = Coordinate(max(bound1.x, bound2.x), max(bound1.y, bound2.y))
        LB = Coordinate(min(bound1.x, bound2.x), min(bound1.y, bound2.y))

        # correct position if out of bounds
        if self.x < LB.x:
            self.x, self.y = UB.x, self.y - 1
            if self.y < LB.y:
                self.y = UB.y
        elif self.x > UB.x:
            self.x, self.y = LB.x, self.y + 1
            if self.y > UB.y:
                self.y = LB.y
        elif self.y < LB.y:
            self.x, self.y = self.x - 1, UB.y
            if self.x < LB.x:
                self.x = UB.x
        elif self.y > UB.y:
            self.x, self.y = self.x + 1, LB.y
            if self.x > UB.x:
                self.x = LB.x


def load_data(dir: str) -> dict[str, Any]:
    data_path = os.path.join("..", f"data\{dir}.json")
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)

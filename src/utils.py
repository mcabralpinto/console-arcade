from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Union
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

    def adjacent(self, other: "Coordinate") -> bool:
        return (self.x == other.x and abs(self.y - other.y) == 1) or (
            self.y == other.y and abs(self.x - other.x) == 1
        )

    def in_bounds(self, bound: "Coordinate") -> bool:
        return 0 <= self.x < bound.x and 0 <= self.y < bound.y
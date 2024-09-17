from enum import Enum
from dataclasses import dataclass


class Status(Enum):
    PRE_GAME = 0
    POST_GAME = 1
    IN_GAME = 2
    IN_REPLAY = 3


@dataclass
class Move2048:
    v: str  # value
    s: tuple[int, int]  # shift

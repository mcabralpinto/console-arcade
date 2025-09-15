from dataclasses import dataclass

from utils import Coordinate


@dataclass
class Move:
    value: str  # value
    shift: Coordinate  # shift

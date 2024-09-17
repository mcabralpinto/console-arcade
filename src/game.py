#work in progress

from dataclasses import dataclass
from typing import Any

@dataclass
class Game:
    arcade: Any
    WIDTH: int
    HEIGHT: int
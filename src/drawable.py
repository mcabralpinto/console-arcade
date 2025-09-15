from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import json
import os
import re

from structs import Coordinate


@dataclass
class Drawable(ABC):
    dim: Coordinate

    # loads data from the a json file
    def load_data(self, dir: str) -> dict[str, Any]:
        data_path = os.path.join("..", f"data\{dir}.json")
        with open(data_path, "r", encoding="utf-8") as file:
            return json.load(file)

    # returns the ANSI escape sequence to move the cursor (x, y) units
    def move(self, x: int, y: int) -> str:
        U, D, R, L = "\033[A", "\033[B", "\033[C", "\033[D"
        return f"{(R if x > 0 else L) * abs(x)}{(D if y > 0 else U) * abs(y)}"

    def start_pos(self) -> None:
        x_pad = (os.get_terminal_size().columns - self.dim.x) // 2
        y_pad = (os.get_terminal_size().lines - self.dim.y - 5) // 2

        print("\033[H" + "\033[B" * y_pad + "\033[C" * x_pad, end="", flush=True)

    # returns a colored string
    def paint(self, string: str, color: str) -> str:
        if color == "":
            return string
        colors = self.load_data("misc")["COLORS"]
        return f"{colors[color]}{string}\033[0m"

    # return a string without ANSI escape sequences
    def strip_ansi(self, s: str) -> str:
        return re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', s)

    # draws the content of the drawable
    @abstractmethod
    def content(self, values) -> None: ...

    # buffer
    def draw(self, values: list[Any] = []) -> None:
        self.data = self.load_data("menu")
        self.start_pos()
        self.content(values)

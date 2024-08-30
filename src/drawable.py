from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List
from status import Status
import json
import os


@dataclass
class Drawable(ABC):
    dim: tuple[int, int]

    # loads data from the data.json file
    def load_data(self) -> Dict[str, Any]:
        with open("..\\data\\data.json", "r", encoding="utf-8") as file:
            return json.load(file)

    # returns the ANSI escape sequence to move the cursor (x, y) units
    def move(self, x: int, y: int) -> str:
        U, D, R, L = "\033[A", "\033[B", "\033[C", "\033[D"
        return f"{(R if x > 0 else L) * abs(x)}{(D if y > 0 else U) * abs(y)}"

    def start_pos(self) -> None:
        x_pad = (os.get_terminal_size().columns - self.dim[0]) // 2
        y_pad = (os.get_terminal_size().lines - self.dim[1] - 5) // 2

        print("\033[H" + "\033[B" * y_pad + "\033[C" * x_pad, end="", flush=True)

    # returns a colored string
    def paint(self, char: str, color: str) -> str:
        colors = self.load_data()["COLORS"]
        return f"{colors[color]}{char}\033[0m"

    # draws the content of the drawable
    @abstractmethod
    def content(self, values) -> None: ...

    # buffer
    def draw(self, values: List[Any] = []) -> None:
        self.start_pos()
        self.data = self.load_data()
        self.content(values)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import json
import os
import re

from utils import Coordinate, load_data


@dataclass
class Drawable(ABC):
    dim: Coordinate
    offset: Coordinate = Coordinate(0, 0)

    # returns the ANSI escape sequence to move the cursor (x, y) units
    @staticmethod
    def move(x: int, y: int) -> str:
        U, D, R, L = "\033[A", "\033[B", "\033[C", "\033[D"
        return f"{(R if x > 0 else L) * abs(x)}{(D if y > 0 else U) * abs(y)}"
    
    def start_pos(self) -> None:
        x_pad = (os.get_terminal_size().columns - self.dim.x) // 2 + self.offset.x
        y_pad = (os.get_terminal_size().lines - self.dim.y - 5) // 2 + self.offset.y

        print("\033[H" + "\033[B" * y_pad + "\033[C" * x_pad, end="", flush=True)

    # returns a colored string
    @staticmethod
    def paint(string: str, color: str = "", bg_color: str = "") -> str:
        if color == "":
            return string
        colors = load_data("misc")
        foreground = f"{colors['COLORS'][color]}" if color else ""
        background = f";{colors['BG_COLORS'][bg_color]}" if bg_color else ""
        return f"\033[{foreground}{background}m{string}\033[0m"

    # return a string without ANSI escape sequences
    @staticmethod
    def strip_ansi(s: str) -> str:
        return re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', s)

    # draws the content of the drawable
    @abstractmethod
    def content(self, values: list[Any]) -> None: ...

    # buffer
    def draw(self, values: list[Any] = []) -> None:
        self.data = load_data("menu")
        self.start_pos()
        self.content(values)

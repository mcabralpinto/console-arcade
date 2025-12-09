from abc import abstractmethod
from dataclasses import dataclass, field
import json
import os
from typing import Any
from pynput.keyboard import KeyCode


@dataclass
class Game:
    arcade: Any
    KEYS: dict[str, list[KeyCode]] = field(default_factory=dict)
    display: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def start(self, *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    def render(self, *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    def on_press(self, key: KeyCode, *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    def run_replay(self) -> None: ...

    @abstractmethod
    def run(self) -> None: ...

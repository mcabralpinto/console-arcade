from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from pynput.keyboard import KeyCode


@dataclass
class Game:
    arcade: Any
    KEYS: dict[str, list[KeyCode]] = field(default_factory=dict)

    @abstractmethod
    def start(self, *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    def on_press(self, key: KeyCode, *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    def run_replay(self) -> None: ...

    @abstractmethod
    def run(self) -> None: ...

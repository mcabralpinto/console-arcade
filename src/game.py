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

    # loads data from the a json file
    def load_data(self, dir: str) -> dict[str, Any]:
        data_path = os.path.join("..", f"data\{dir}.json")
        with open(data_path, "r", encoding="utf-8") as file:
            return json.load(file)

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

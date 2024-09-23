from dataclasses import dataclass, field
from typing import Any, Union
from pynput.keyboard import Key, KeyCode


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

# cd git\console-arcade && .\env\Scripts\activate && cd src && python main.py

import os
import json
import re
import time
import threading
from drawable_arcade import Border, Transition, Menu
from abalone import Abalone
from status import Status
from typing import List, Tuple, Any, Dict
from pynput.keyboard import Key, KeyCode
from datetime import datetime
from pynput.keyboard import Listener

# U, D, R, L = "\033[A", "\033[B", "\033[C", "\033[D"


class Arcade:
    def __init__(self, w: int, h: int) -> None:
        self.listener = Listener(on_press=self.on_press)  # key input listener
        self.data: Dict[str, Any] = self.load_data()  # data.json content
        self.title: str = "MAIN"  # current menu title
        self.option: int = 0  # option number. indexes the self.data.OPTS tuple
        self.game: int = 0  # game id. indexes the self.data.GAMES tuple
        self.curr: Any = None  # current game instance
        self.status: Status = Status.PRE_GAME  # current status
        self.replay_vector: List[KeyCode] = []  # stores keys pressed during games

        self.border: Border = Border(dim=(w, h)) 
        self.transition: Transition = Transition(dim=(w, h))
        self.menu: Menu = Menu(dim=(w, h))

        self.WIDTH: int = w
        self.HEIGHT: int = h  # border dimensions
        self.GAMES: Tuple[Any] = (Abalone,)  # game classes

    # loads data from the data.json file
    def load_data(self) -> Dict[str, Any]:
        with open("..\\data\\data.json", "r", encoding="utf-8") as file:
            return json.load(file)

    # converts a key array's elements from string to pynput.keyboard.Key
    def str_to_key(self, keys: List[str]) -> List[KeyCode]:
        key_mapping = {
            "space": Key.space,
            "up": Key.up,
            "down": Key.down,
            "right": Key.right,
            "left": Key.left,
        }
        return [key_mapping[key] for key in keys]

    # converts a key array's elements from pynput.keyboard.Key to string
    def key_to_str(self, keys: List[KeyCode]) -> List[str]:
        return [str(key).replace("Key.", "") for key in keys]

    # handles key presses
    def on_press(self, key: Key | KeyCode | None) -> None:
        try:
            if self.status == Status.IN_GAME:
                self.curr.on_press(key)

            else:
                game = self.data["OPTS"]["MAIN"][self.game - 1].upper()
                opts = (
                    (
                        (("RE_" if self.status == Status.POST_GAME else "") + "GAME")
                        if self.title != "REPLAYS"
                        else ("RE_" + game)
                    )
                    if self.title != "MAIN"
                    else "MAIN"
                )

                if key in (Key.up, Key.down) and self.status != Status.IN_REPLAY:
                    self.option += (
                        (1 if self.option < len(self.data["OPTS"][opts]) - 1 else 0)
                        if key == Key.down
                        else (-1 if self.option > 0 else 0)
                    )
                    self.menu.draw(
                        [self.title, self.option, self.game, self.curr, self.status]
                    )

                if key == Key.space and self.status != Status.IN_REPLAY:
                    opt_text = self.data["OPTS"][opts][self.option]

                    if self.game == 0:
                        if self.option < 1:
                            self.transition.draw()
                            self.game = self.option + 1
                            self.title = list(self.data["MENUS"])[self.game]
                            self.curr = self.GAMES[self.game - 1](
                                self, self.WIDTH, self.HEIGHT
                            )
                        elif opt_text == "Exit":
                            self.listener.stop()

                    else:
                        if opt_text in ["Play Game", "Play Again"]:
                            self.transition.draw()
                            self.status = Status.IN_GAME
                            self.option = 0
                            self.curr.run()

                        elif opt_text == "Save Replay" and self.replay_vector != []:
                            vect = self.key_to_str(self.replay_vector)
                            re_game = (
                                "RE_" if self.status == Status.POST_GAME else ""
                            ) + game
                            replay_str = self.menu.replay_str(self.curr.scores)

                            with open(
                                "..\\data\\data.json", "r+", encoding="utf-8"
                            ) as file:
                                data = json.load(file)
                                data["REPLAYS"][game].reverse()
                                data["REPLAYS"][game].append(vect)
                                data["REPLAYS"][game].reverse()
                                data["OPTS"][re_game].reverse()
                                data["OPTS"][re_game].append(replay_str)
                                data["OPTS"][re_game].reverse()
                                file.seek(0)
                                json.dump(data, file, indent=4)
                                file.truncate()

                            self.replay_vector = []
                            self.data = self.load_data()

                        elif opt_text == "Replays":
                            if len(self.data["REPLAYS"][game]) > 0:
                                self.transition.draw()
                                self.title = "REPLAYS"
                                self.option = 0

                        elif opt_text == "Return":
                            self.transition.draw()
                            if self.title == "REPLAYS":
                                self.title = game
                            else:
                                self.title = "MAIN"
                                self.game = 0
                                self.curr = None
                            self.option = 0
                            self.status = Status.PRE_GAME

                        elif self.title == "REPLAYS":
                            self.transition.draw()
                            self.status = Status.IN_REPLAY
                            vect = self.data["REPLAYS"][game][self.option]
                            self.replay_vector = self.str_to_key(vect)
                            self.option = 0
                            self.curr.run()
                            threading.Thread(target=self.curr.run_replay).start()

                    if self.status not in (Status.IN_GAME, Status.IN_REPLAY):
                        self.menu.draw(
                            [self.title, self.option, self.game, self.curr, self.status]
                        )

                elif key == Key.esc:
                    if self.game == 0:
                        self.listener.stop()
                    else:
                        replay = False
                        if self.status == Status.IN_REPLAY:
                            self.status = Status.PRE_GAME
                            replay = True
                        self.transition.draw()
                        if not replay:
                            if self.title == "REPLAYS":
                                self.title = game
                                self.option = 0
                            else:
                                self.title = "MAIN"
                                self.game = 0
                                self.option = 0
                                self.curr = None
                                self.status = Status.PRE_GAME
                        self.menu.draw(
                            [
                                self.title,
                                self.option,
                                self.game,
                                self.curr,
                                self.status,
                            ]
                        )
        except AttributeError:
            pass

    # runs the arcade
    def run(self) -> None:
        try:
            self.border.draw()
            self.menu.draw([self.title, self.option, self.game, self.curr, self.status])
            self.listener.start()
            self.listener.join()
        except KeyboardInterrupt:
            pass

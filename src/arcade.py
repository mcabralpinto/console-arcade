# cd git\console-arcade && .\env\Scripts\activate && cd src && python main.py
from arcade_drawable import Border, Transition, Menu
from abalone import Abalone
from tzfe import TZFE
from structs import Status
from game_info import GameInfo

import os
import json
import threading
from typing import Any
from dataclasses import dataclass, field
from pynput.keyboard import Key, KeyCode, Listener

# U, D, R, L = "\033[A", "\033[B", "\033[C", "\033[D"


@dataclass
class Arcade:
    # data: dict[str, Any] = None  # data.json content
    title: str = "MAIN"  # current menu title
    opt: int = 0  # option number. indexes the self.data.OPTS tuple
    game: int = 0  # game id. indexes the self.data.GAMES tuple
    curr: Any = None  # current game instance
    status: Status = Status.PRE_GAME  # current status
    game_info: GameInfo = field(default_factory=GameInfo)  # stores info for replays

    GAMES: list[Any] = field(default_factory=lambda: [Abalone, TZFE])  # game classes

    border: Border = field(default_factory=lambda: Border(dim=(36, 21)))
    transition: Transition = field(default_factory=lambda: Transition(dim=(36, 21)))
    menu: Menu = field(default_factory=lambda: Menu(dim=(36, 21)))

    def __post_init__(self):
        self.listener = Listener(on_press=self.on_press)  # key input listener
        self.data: dict[str, Any] = self.load_data()  # data.json content

    # loads data from the data.json file
    def load_data(self) -> dict[str, Any]:
        data_path = os.path.join("..", "data", "data.json")
        with open(data_path, "r", encoding="utf-8") as file:
            return json.load(file)

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
                    self.opt += (
                        (1 if self.opt < len(self.data["OPTS"][opts]) - 1 else 0)
                        if key == Key.down
                        else (-1 if self.opt > 0 else 0)
                    )
                    self.menu.draw(
                        [self.title, self.opt, self.game, self.curr, self.status]
                    )

                if key == Key.space and self.status != Status.IN_REPLAY:
                    opt_text = self.data["OPTS"][opts][self.opt]

                    if self.game == 0:
                        if self.opt < 2:
                            self.transition.draw()
                            self.game = self.opt + 1
                            self.title = list(self.data["MENUS"])[self.game + 1]
                            self.curr = self.GAMES[self.game - 1](arcade=self)
                            self.opt = 0
                        elif opt_text == "Exit":
                            self.listener.stop()

                    else:
                        if opt_text in ["Play Game", "Play Again"]:
                            self.transition.draw()
                            self.status = Status.IN_GAME
                            self.opt = 0
                            self.curr.run()

                        elif opt_text == "Save Replay" and self.game_info.keys != []:
                            stored_info = self.game_info.data_to_str()
                            re_game = (
                                "RE_" if self.status == Status.POST_GAME else ""
                            ) + game
                            replay_str = self.menu.replay_str(self.game_info.score)

                            with open(
                                "..\\data\\data.json", "r+", encoding="utf-8"
                            ) as file:
                                data = json.load(file)
                                data["REPLAYS"][game].reverse()
                                data["REPLAYS"][game].append(stored_info)
                                data["REPLAYS"][game].reverse()
                                data["OPTS"][re_game].reverse()
                                data["OPTS"][re_game].append(replay_str)
                                data["OPTS"][re_game].reverse()
                                file.seek(0)
                                json.dump(data, file, indent=4)
                                file.truncate()

                            self.game_info.clear()
                            self.data = self.load_data()

                        elif opt_text == "Replays":
                            if len(self.data["REPLAYS"][game]) > 0:
                                self.transition.draw()
                                self.title = "REPLAYS"
                                self.opt = 0

                        elif opt_text == "Return":
                            self.transition.draw()
                            if self.title == "REPLAYS":
                                self.title = game
                            else:
                                self.title = "MAIN"
                                self.game = 0
                                self.curr = None
                            self.opt = 0
                            self.status = Status.PRE_GAME

                        elif self.title == "REPLAYS":
                            self.transition.draw()
                            self.status = Status.IN_REPLAY
                            stored_info = self.data["REPLAYS"][game][self.opt]
                            self.game_info.str_to_data(stored_info)
                            self.opt = 0
                            self.curr.run()
                            threading.Thread(target=self.curr.run_replay).start()

                    if self.status not in (Status.IN_GAME, Status.IN_REPLAY):
                        self.menu.draw(
                            [self.title, self.opt, self.game, self.curr, self.status]
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
                                self.opt = 0
                            else:
                                self.title = "MAIN"
                                self.game = 0
                                self.opt = 0
                                self.curr = None
                                self.status = Status.PRE_GAME
                        self.menu.draw(
                            [self.title, self.opt, self.game, self.curr, self.status]
                        )
        except AttributeError:
            pass

    # runs the arcade
    def run(self) -> None:
        try:
            self.border.draw()
            self.menu.draw([self.title, self.opt, self.game, self.curr, self.status])
            self.listener.start()
            self.listener.join()
        except KeyboardInterrupt:
            pass

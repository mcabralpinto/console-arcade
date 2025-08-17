# cd git\console-arcade && .\env\Scripts\activate && cd src && python main.py
from arcade.arcade_drawable import Border, Transition, Menu
from abalone.abalone import Abalone
from tzfe.tzfe import TZFE
from structs import Status, GameInfo

import os
import json
import threading
from typing import Any
from dataclasses import dataclass, field
from pynput.keyboard import Key, KeyCode, Listener

# U, D, R, L = "\033[A", "\033[B", "\033[C", "\033[D"


@dataclass
class Arcade:
    title: str = "MAIN"  # current menu title
    opt: int = 0  # option number. indexes the self.data.OPTS tuple
    game: int = 0  # game id. indexes the self.data.GAMES tuple
    curr: Any = None  # current game instance
    status: Status = Status.PRE_GAME  # current status
    game_info: GameInfo = field(default_factory=GameInfo)  # stores info for replays

    # game classes
    GAMES: list[Any] = field(default_factory=lambda: [Abalone, TZFE])

    border: Border = field(default_factory=lambda: Border(dim=(36, 21)))
    transition: Transition = field(default_factory=lambda: Transition(dim=(36, 21)))
    menu: Menu = field(default_factory=lambda: Menu(dim=(36, 21)))

    def __post_init__(self):
        self.listener = Listener(on_press=self.on_press)  # key input listener
        self.data: dict[str, Any] = self.load_data("menu")  # menu.json content

    # loads data from the a json file
    def load_data(self, dir: str) -> dict[str, Any]:
        data_path = os.path.join("..", f"data\{dir}.json")
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

                            # save replay data to the game's replay file
                            replay_file = f"..\\data\\replays\\{game.lower()}.json"
                            with open(replay_file, "r+", encoding="utf-8") as file:
                                replay_data = json.load(file)
                                replay_data.insert(0, stored_info)
                                file.seek(0)
                                json.dump(replay_data, file, indent=4)
                                file.truncate()

                            # save replay option string to menu.json
                            menu_file = "..\\data\\menu.json"
                            with open(menu_file, "r+", encoding="utf-8") as file:
                                menu_data = json.load(file)
                                menu_data["OPTS"][re_game].insert(0, replay_str)
                                file.seek(0)
                                json.dump(menu_data, file, indent=4)
                                file.truncate()

                            self.game_info.clear()

                        elif opt_text == "Replays":
                            self.data = self.load_data("menu")
                            replays = self.load_data(f"replays\\{game.lower()}")
                            if len(replays) > 0:
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
                            stored_info = self.load_data(f"replays\\{game.lower()}")[
                                self.opt
                            ]
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

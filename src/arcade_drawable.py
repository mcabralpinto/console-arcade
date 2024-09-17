from drawable import Drawable
from structs import Status
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime
import re
import time
import os


@dataclass
class Border(Drawable):
    # draws the arcade border
    def content(self, _) -> None:
        W, H = self.dim[0], self.dim[1]
        x_pad = (os.get_terminal_size().columns - W) // 2
        c = " " * (x_pad - 1)

        print(self.move(-1, -1), end="", flush=True)
        print(
            f"╭{'─' * W}╮\n"
            + f"{c}│{self.move(W, 0)}│\n" * H
            + f"{c}├{'─' * W}┤\n"
            + f"{c}│{self.move(W // 2, 0)}△{self.move((W - 1) // 2, 0)}│\n"
            + f"{c}│{self.move((W - 4) // 2, 0)}◁ ◯ ▷{self.move((W - 5) // 2, 0)}│\n"
            + f"{c}│{self.move(W // 2, 0)}▽{self.move((W - 1) // 2, 0)}│\n"
            + f"{c}╰{'─' * W}╯"
            + f"{self.move(-W - 1, -H - 4)}",
            end="",
        )


@dataclass
class Transition(Drawable):
    # draws half a transition effect
    def half(self, char: str) -> None:
        W, H = self.dim[0], self.dim[1]
        oob = False
        offset = W // W
        rest = 1 if W // offset == 0 else 0

        x = 0
        for i in range(H + W // offset - rest):
            y = max(0, i - W // offset + 1)

            while True:
                if offset > W - x:
                    oob = True
                    y -= 1
                print(char * (min(offset, W - x)), end="", flush=True)
                x += offset
                if (x - (2 * offset) < 0) or (y + 1 == H):
                    break
                extra = (W % offset) if oob else offset
                print(self.move(-(offset + extra), 1), end="", flush=True)
                oob = False
                x -= 2 * offset
                y += 1

            while (x + offset < W) and (y - 1 >= 0):
                print(self.move(offset, -1), end="", flush=True)
                x += offset
                y -= 1

            time.sleep(0.005)

    # draws a transition effect
    def content(self, _) -> None:
        self.half("█")
        self.start_pos()
        self.half(" ")


@dataclass
class Menu(Drawable):
    title: str = field(default_factory=str)
    option: int = field(default_factory=int)
    game: int = field(default_factory=int)
    curr: Any = None
    status: Status = Status.PRE_GAME

    def update(self, values: list[Any]) -> None:
        self.title, self.option, self.game, self.curr, self.status = values

    # returns the length of a string without ANSI escape sequences
    def pure_len(self, text: str) -> int:
        ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
        return len(ansi_escape.sub("", text))

    # returns the string representation of the current game in the replay menu
    def replay_str(self, info: Any) -> str:
        date = datetime.now().strftime("%d-%m-%Y")
        hour = datetime.now().strftime("%H:%M")
        if self.game == 1:  # Abalone
            return (
                self.paint(info["R"], "RED")
                + " - "
                + self.paint(info["B"], "BLUE")
                + f" · {hour} · {date}"
            )
        return ""

    # returns the title of the current menu
    def menu_title(self) -> str:
        W = self.dim[0]
        R, N = "\033[C", self.move(-W, 1)
        ML = max(len(s) for s in self.data["MENUS"][self.title])

        final = ""
        for t in self.data["MENUS"][self.title]:
            final += (
                R * ((W - (ML - 1)) // 2)
                + t
                + R * ((W - ML + 2 * (ML - len(t))) // 2)
                + N
            )

        return final

    # returns the score string for the previous game
    def menu_post_game(self) -> str:
        W = self.dim[0]
        D, R, N = "\033[B", "\033[C", self.move(-W, 1)

        if self.status != Status.POST_GAME or self.title == "REPLAYS":
            return ""
        elif self.game == 1:
            RED = self.paint(self.curr.scores["R"], "RED")
            BLUE = self.paint(self.curr.scores["B"], "BLUE")
            return f"{D}{R * ((W - 5) // 2)}{RED} - {BLUE}{R * ((W - 4) // 2)}{N}"
        elif self.game == 2:
            L = len(str(self.curr.score))
            return f"{D}{R * ((W - L) // 2)}{self.curr.score}{R * ((W - L + 1) // 2)}{N}"
        return ""

    # returns the option string for the current menu
    def menu_list(self) -> str:
        W, B = self.dim[0], 14 if self.title != "REPLAYS" else 26
        D, N = "\033[B", self.move(-W, 1)
        space = 6 if self.status != Status.POST_GAME or self.title == "REPLAYS" else 8
        opt_n = (2 * ((l := self.dim[1] - space) // 4)) + 1
        idxs = [2 * i + (1 if l % 4 > 1 else 0) for i in range(opt_n)]

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

        final = ""
        for i in range(l):
            if i in idxs:
                cond = (curr := self.option + (i - opt_n + 1) // 2) < 0 or curr >= len(
                    self.data["OPTS"][opts]
                )
                final += (
                    " " * ((W - B) // 2)
                    + ("> " if curr == self.option else "")
                    + ("" if cond else self.data["OPTS"][opts][curr])
                    + " "
                    * (
                        (W + ((B - 3) if curr == self.option else (B + 1))) // 2
                        - (0 if cond else self.pure_len(self.data["OPTS"][opts][curr]))
                    )
                    + N
                )
            else:
                final += D

        return final

    # draws the current menu state
    def content(self, values: list[Any]) -> None:
        self.update(values)
        W, H = self.dim[0], self.dim[1]
        R, N = "\033[C", self.move(-W, 1)

        print(
            self.menu_title()
            + f"{R * ((W - 14) // 2)}{'─' * 14}{R * ((W - 13) // 2)}{N}"
            + self.menu_post_game()
            + f"{R * W}{N}"
            + self.menu_list()
            + f"{R * W}",
            end="",
            flush=True,
        )

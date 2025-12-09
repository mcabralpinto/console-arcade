# cd git\console-arcade && .\env\Scripts\activate && cd src && python main.py
import os
import sys
import ctypes
from arcade.arcade import Arcade
from abalone.abalone import Abalone
from tzfe.tzfe import TZFE
from scrabble.scrabble import Scrabble
from carcassonne.carcassonne import Carcassonne

if os.name == "nt":
    import msvcrt
else:
    import select


class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_int), ("bVisible", ctypes.c_bool)]


def hide_cursor():
    if os.name == "nt":  # Windows
        SetConsoleCursorInfo = ctypes.windll.kernel32.SetConsoleCursorInfo
        GetStdHandle = ctypes.windll.kernel32.GetStdHandle
        STD_OUTPUT_HANDLE = -11

        console_output = GetStdHandle(STD_OUTPUT_HANDLE)

        cursor_info = CONSOLE_CURSOR_INFO()
        cursor_info.dwSize = 1
        cursor_info.bVisible = False

        SetConsoleCursorInfo(console_output, ctypes.byref(cursor_info))
    else:  # Unix-like (Linux, macOS)
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()


def show_cursor():
    if os.name == "nt":  # Windows
        SetConsoleCursorInfo = ctypes.windll.kernel32.SetConsoleCursorInfo
        GetStdHandle = ctypes.windll.kernel32.GetStdHandle
        STD_OUTPUT_HANDLE = -11

        console_output = GetStdHandle(STD_OUTPUT_HANDLE)

        cursor_info = CONSOLE_CURSOR_INFO()
        cursor_info.dwSize = 1
        cursor_info.bVisible = True

        SetConsoleCursorInfo(console_output, ctypes.byref(cursor_info))
    else:  # Unix-like (Linux, macOS)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def clear_console():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Unix-like (Linux, macOS)
        os.system("clear")


def main():
    try:
        hide_cursor()
        clear_console()

        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            match arg:
                case "abalone":
                    game = Abalone(None)
                    game.run()
                case "2048":
                    game = TZFE(None)
                    game.run()
                case "scrabble":
                    game = Scrabble(None)
                    game.run()
                case "carcassonne":
                    game = Carcassonne(None)
                    game.run()
                case _:
                    arcade = Arcade()
                    arcade.run()
        else:
            arcade = Arcade()
            arcade.run()

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        #clear_console()


if __name__ == "__main__":
    main()

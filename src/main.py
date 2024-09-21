import os
import sys
import ctypes
from arcade import Arcade


class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_int), ("bVisible", ctypes.c_bool)]


def hide_cursor():
    if os.name == 'nt':  # Windows
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
    if os.name == 'nt':  # Windows
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
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def main():
    W, H = 36, 21
    hide_cursor()
    clear_console()
    arcade = Arcade(W, H)
    arcade.run()
    show_cursor()


if __name__ == "__main__":
    main()

import os
import ctypes
from arcade import Arcade


class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_int), ("bVisible", ctypes.c_bool)]


def hide_cursor():
    SetConsoleCursorInfo = ctypes.windll.kernel32.SetConsoleCursorInfo
    GetStdHandle = ctypes.windll.kernel32.GetStdHandle
    STD_OUTPUT_HANDLE = -11

    console_output = GetStdHandle(STD_OUTPUT_HANDLE)

    cursor_info = CONSOLE_CURSOR_INFO()
    cursor_info.dwSize = 1
    cursor_info.bVisible = False

    SetConsoleCursorInfo(console_output, ctypes.byref(cursor_info))


def main():
    W, H = 36, 21
    hide_cursor()
    os.system("cls")
    arcade = Arcade(W, H)
    arcade.run()


if __name__ == "__main__":
    main()

# Console Arcade

Console Arcade is a Python-based project I've been working that includes an ever-expanding collection of classic games in a console environment, and a menu system to navigate through them. Additional features, such as replays, are also to be implemented.

## Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/mcabralpinto/console-arcade.git
    cd console-arcade
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv env
    ```

3. **Activate the virtual environment:**
    - **Windows:**
        ```sh
        .\env\Scripts\activate
        ```
    - **Unix or MacOS:**
        ```sh
        source env/bin/activate
        ```

4. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. **Navigate to the [`src`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FUtilizador%2Fgit%2Fconsole-arcade%2Fsrc%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22eac2b851-7904-4c88-88fc-04a240d03d6b%22%5D "c:\Users\Utilizador\git\console-arcade\src") directory:**
    ```sh
    cd src
    ```

2. **Run the main script:**
    To run the arcade menu, run it normally:

    ```sh
    python main.py
    ```

    To run a specific game, pass its name as an argument after the command. Currently the supported games are:

    ```sh
    abalone
    2048
    scrabble
    ```

## Project Components

### Arcade

The arcade module contains the core menu system and navigation logic for the console arcade.
The main `Arcade` class at [`arcade.py`](src/arcade/arcade.py) handles menu navigation, game launching, replay management, and keyboard input processing.

### Abstract Game Classes

There are two main classes which every game inherits: the base class `Game` (at [`game.py`](src/game.py)), which defines the common interface for all games in the arcade, and `Drawable` (at [`drawable.py`](src/drawable.py)), which provides methods for rendering game elements.

### Abalone

Two-player board game where players attempt to push each other's marbles off the board. The entire logic of the game, including piece movement mechanics and move validation, was implemented from scratch.

### 2048 (TFZE)

A console spin on a viral web game whose goal is to combine numbered tiles on a 4x4 grid. It also features an attempt at smooth sliding tile animations in a console environment.

### Scrabble

Classic board game where players use letter tiles to create words on a grid, scoring based on the sum of the tile values and existing modifiers. This implementation includes all basic mechanics such as tile placement, exchanging tiles, and challenging words. Not playable from the arcade menu yet.

### Data

Contains relevant game data in JSON format, including pre-loaded graphics, special characters, and replay data for all of the available games.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.
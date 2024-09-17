# Console Arcade

Console Arcade is a Python-based project I've been working that includes an ever-expanding collection of classic games in a console environment, and a menu system to navigate through them. Additional features, such as replays, are also to be implemented.

## Setup

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
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
    ```sh
    python main.py
    ```

## Project Components

### [`src/main.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FUtilizador%2Fgit%2Fconsole-arcade%2Fsrc%2Fmain.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22eac2b851-7904-4c88-88fc-04a240d03d6b%22%5D "c:\Users\Utilizador\git\console-arcade\src\main.py")

The entry point of the application. It initializes and runs the `Arcade` class.

### [`src/arcade.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FUtilizador%2Fgit%2Fconsole-arcade%2Fsrc%2Farcade.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22eac2b851-7904-4c88-88fc-04a240d03d6b%22%5D "c:\Users\Utilizador\git\console-arcade\src\arcade.py")

The `Arcade` class is the central class throughout the app. It ties all of its functionalities together, handling the menu system logic, running games and replays, and loading necessary data.

- **Main Methods:**
  - `run`: Boots up the arcade and initializes the keypress reading system.
  - `on_press`: The program's keypress handler. When a game is running, redirects keypresses to its `on_press` function.
  - `load_data`: Loads data from `data.json`.

### [`src/drawable.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FUtilizador%2Fgit%2Fconsole-arcade%2Fsrc%2Fdrawable.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22eac2b851-7904-4c88-88fc-04a240d03d6b%22%5D "c:\Users\Utilizador\git\console-arcade\src\drawable.py") and subclasses

The `Drawable` class is an abstract base class for drawable objects in the console. Its primary function is to draw content and control the cursor position.

- **Main Methods:**
  - `draw`: Draws the content of the drawable.
  - `move` & `start_pos`: Allow for moving the cursor during the drawing process.

### [`data/data.json`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FUtilizador%2Fgit%2Fconsole-arcade%2Fdata%2Fdata.json%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22eac2b851-7904-4c88-88fc-04a240d03d6b%22%5D "c:\Users\Utilizador\git\console-arcade\data\data.json")

Contains the static data which is used while the program is running, such as menu options and titles, replay details, and other relevant information.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Contact

For any inquiries, please contact the project maintainer.

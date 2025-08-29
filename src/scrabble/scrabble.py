import random
from game import Game
from scrabble.scrabble_drawable import Board
from structs import TileScrabble, Status, Coordinate

from dataclasses import dataclass
from pynput.keyboard import Key, KeyCode
from typing import Any
from copy import copy, deepcopy


@dataclass
class Scrabble(Game):
    def __post_init__(self):
        self.display = {"BOARD": Board(dim=(61, 31))}
        self.KEYS = {"MOVE": [Key.up, Key.down, Key.left, Key.right]}  # key mapping
        self.standalone = self.arcade is None
        self.running = True

    def start(self) -> None:
        self.data: dict[Any] = self.load_data("games\\scrabble")
        self.dictionary: dict[str, list[str]] = self.load_data("games\\scrabble_words")
        random.shuffle(self.data["LETTERS"])

        # game board
        self.board: list[list[TileScrabble | None]] = [[None] * 15 for _ in range(15)]

        # cursor position
        self.cursor: Coordinate = Coordinate(x=7, y=7)

        # each player's score and tiles
        self.scores: dict[int, int] = {0: 0, 1: 0}
        self.tiles: dict[int, dict[str, list[TileScrabble]]] = {
            0: {"HAND": [], "PLAY": []},
            1: {"HAND": [], "PLAY": []},
        }
        [self.fill_hand(self.tiles[player]["HAND"]) for player in [0, 1]]

        # latest turn information (for challenging)
        self.new_words: list[str] = []
        self.play_score: int = 0

        # game variables
        self.turn: int = 1
        self.direction: bool = True  # True if the write direction is horizontal
        self.exchange: bool = False  # True if the player wants to exchange tiles

        # if not self.standalone and self.arcade.status != Status.IN_REPLAY:
        #     self.arcade.game_info.data["CELLS"] = []

    def render(self) -> None:
        current_play_score = (
            self.score_play(
                self.tiles[self.turn % 2]["PLAY"],
                self.get_play_direction(),
                display=True,
            )
            if not self.exchange
            else 0
        )

        self.display["BOARD"].draw(
            [
                self.board,
                self.cursor,
                self.scores,
                self.tiles,
                self.new_words,
                self.turn,
                self.direction,
                self.exchange,
                current_play_score,
                len(self.data["LETTERS"]),
            ]
        )

    def change_turn(self) -> None:
        self.turn += 1
        self.tiles[self.turn % 2]["PLAY"].clear()
        self.fill_hand(self.tiles[self.turn % 2]["HAND"])

    def fill_hand(self, hand: list[TileScrabble]) -> None:
        while len(hand) < 7 and self.data["LETTERS"]:
            letter = self.data["LETTERS"].pop(0)
            hand.append(TileScrabble(letter=letter, value=self.data["VALUES"][letter]))

    def get_next_position(self, key: KeyCode, delete: bool = False) -> tuple[int, int]:
        x, y = self.cursor
        move_idx = self.KEYS["MOVE"].index(key)
        dx, dy = ((0, -1), (0, 1), (-1, 0), (1, 0))[move_idx]

        # try to find a valid position
        while True:
            new_x, new_y = x + dx, y + dy

            if dx != 0:
                if new_x < 0:
                    new_x = 14
                    new_y = (y - 1) % 15
                elif new_x >= 15:
                    new_x = 0
                    new_y = (y + 1) % 15

            if dy != 0:
                if new_y < 0:
                    new_y = 14
                    new_x = (x - 1) % 15
                elif new_y >= 15:
                    new_y = 0
                    new_x = (x + 1) % 15

            tile = self.board[new_y][new_x]
            if tile is None or (delete and tile and not tile.locked):
                return new_x, new_y

            x, y = new_x, new_y

    def get_play_direction(self) -> bool:
        # no tiles played
        if not (play := self.tiles[self.turn % 2]["PLAY"]):
            return True

        # one tile played
        P0 = play[0].position
        if len(play) == 1:
            # horizontal if there are any horizontal neighbors
            return self.board[P0.y][P0.x - 1] or self.board[P0.y][P0.x + 1]

        # more than one tile played
        P1 = play[1].position if len(play) > 1 else None
        return P0.y == P1.y

    def adjacent_positions(
        self,
        new: Coordinate,
        placed: list[TileScrabble],
    ) -> bool:
        new = deepcopy(new)

        # check alignment
        if new.x == placed[0].position.x:
            move = (0, 1) if new.y < placed[0].position.y else (0, -1)
        elif new.y == placed[0].position.y:
            move = (1, 0) if new.x < placed[0].position.x else (-1, 0)
        else:
            return False

        # check adjacency
        while not new.adjacent(placed[0].position):
            new += move
            if (
                not new.in_bounds(Coordinate(15, 15))
                or self.board[new.y][new.x] is None
            ):
                return False

        # passed!
        return True

    def check_tile_validity(self, key: KeyCode) -> TileScrabble:
        play = self.tiles[self.turn % 2]["PLAY"]
        hand = self.tiles[self.turn % 2]["HAND"]
        C = self.cursor

        # # check first turn constraint
        # if self.turn == 1 and not (C.x == 7 or C.y == 7):
        #     return None

        # check board availability
        # if self.board[C.y][C.x] is not None:
        #     return None

        # check position correctness
        if not self.exchange:
            if len(play) > 1:
                P1 = play[0].position
                # check alignment to the rest of the play
                if self.get_play_direction():
                    if not C.y == P1.y:
                        return None
                else:
                    if not C.x == P1.x:
                        return None
            if len(play) > 0:
                # check adjacency to rest of the play
                if not self.adjacent_positions(C, play):
                    return None

        # check existence (of said letter or a blank)
        for tile in hand:
            if tile.letter == key.char.upper():
                return tile
        for tile in hand:
            if tile.value == 0:
                tile.letter = key.char.upper()
                return tile

        return None

    def check_play_validity(self) -> bool:
        T = self.tiles[self.turn % 2]
        last_turn = (self.turn - 1) % 2

        if len(T["PLAY"]) < 2:
            return False
        
        # no letter has been played
        if len(self.data["LETTERS"]) == 86 and not self.tiles[last_turn]["PLAY"]:
            # check if touching center of the board
            if any(tile.position == (7, 7) for tile in T["PLAY"]):
                return True
        else:
            # check if touching any other already placed tile
            for tile in T["PLAY"]:
                if tile.has_neighbor(self.board, locked=True):
                    return True

        return False

    def score_play(
        self, play: list[TileScrabble], direction, branch=True, display=False
    ):
        # check whether it's a play or a pass
        if not play:
            return 0

        # movement and position variables
        if direction:
            play.sort(key=lambda t: t.position.x)
            move = (1, 0)
        else:
            play.sort(key=lambda t: t.position.y)
            move = (0, 1)
        current_position = copy(play[0].position)
        reverse_move = (-move[0], -move[1])

        # determine word starting position
        while current_position.in_bounds(Coordinate(15, 15)):
            test_pos = current_position + reverse_move
            if (
                test_pos.in_bounds(Coordinate(15, 15))
                and self.board[test_pos.y][test_pos.x] is not None
            ):
                current_position = test_pos
            else:
                break

        # score variables
        multiplier = 1
        score = 0
        overlap_score = 0
        word = ""

        # determine word score
        while current_position.in_bounds(Coordinate(15, 15)) and (
            tile := self.board[current_position.y][current_position.x]
        ):
            # score overlapping words
            if branch and not tile.locked:
                overlap_score += self.score_play([tile], not direction, False, display)

            # account for letter multipliers
            value = tile.value
            M = self.data["MULTIPLIERS"]
            cell = self.data["BOARD"][current_position.y][current_position.x]
            if cell in M and not tile.locked:
                m = M[cell]
                value *= m[0]
                multiplier *= m[1]

            # update info
            score += value
            word += tile.letter
            current_position += move

        # apply word multiplier
        score *= multiplier

        # discard single tile "overlapping" plays
        if len(word) == 1 and not branch:
            return 0

        # apply bingo bonus
        if branch and len(play) == 7:
            score += 50

        # add new word to self.new_words
        if word and word not in self.new_words and not display:
            self.new_words.append(word)

        total_score = score + overlap_score
        return total_score

    def on_press(self, key: KeyCode) -> None:
        C = self.cursor
        T = self.tiles[self.turn % 2]
        try:
            if key in self.KEYS["MOVE"]:
                # move cursor
                new_x, new_y = self.get_next_position(key)
                self.cursor = Coordinate(new_x, new_y)

            elif hasattr(key, "char") and key.char and key.char.isalpha():
                # check if it's a valid write
                if tile := self.check_tile_validity(key):
                    # place tile on board
                    tile.position = Coordinate(C.x, C.y)
                    self.board[C.y][C.x] = tile

                    # update hand
                    T["PLAY"].append(tile)
                    T["HAND"].remove(tile)

                    if not self.exchange:
                        # move cursor
                        self.on_press(Key.right if self.direction else Key.down)

            elif key == Key.backspace:
                # determine direction to move
                move_key = Key.left if self.direction else Key.up
                x, y = self.get_next_position(move_key, delete=True)

                # check if valid slot for deletion
                tile = self.board[y][x]
                if not (tile and not tile.locked and tile in T["PLAY"]):
                    return

                # clear tile position
                self.board[y][x] = None

                # update hand
                if tile.value == 0:
                    tile.letter = "*"
                T["PLAY"].remove(tile)
                T["HAND"].append(tile)

                # move cursor
                tile.position = Coordinate(-1, -1)
                self.cursor = Coordinate(x, y)

            elif key == KeyCode.from_char("1"): # confirm play
                if T["PLAY"]:
                    # make sure the play is valid
                    if not self.check_play_validity():
                        return

                    # clear last play's new words
                    self.new_words.clear()

                    # score play
                    self.play_score = self.score_play(
                        T["PLAY"],
                        self.get_play_direction(),
                    )
                    self.scores[self.turn % 2] += self.play_score

                    # lock play slots
                    for tile in T["PLAY"]:
                        tile.locked = True

                # change turn
                self.change_turn()

            elif key == KeyCode.from_char("2"): # exchange tiles
                if not self.exchange:
                    # only activate exchange if no tiles are played
                    if not T["PLAY"]:
                        self.exchange = True
                else:
                    # if no tiles selected, cancel the exchange
                    if T["PLAY"]:
                        # return tiles to bag
                        for tile in T["PLAY"]:
                            self.data["LETTERS"].append(tile.letter)

                        # refill the player's hand
                        self.fill_hand(T["HAND"])
                        T["PLAY"].clear()

                        # change turn
                        self.turn += 1
                    self.exchange = False

            elif key == KeyCode.from_char("3"): # challenge word
                if not T["PLAY"] and self.new_words:
                    success = False
                    # see if any new words are not valid
                    for word in self.new_words:
                        if word not in self.dictionary[word[0]]:
                            last_turn = (self.turn - 1) % 2

                            # remove the tiles from the board
                            for tile in self.tiles[last_turn]["PLAY"]:
                                self.board[tile.position.y][tile.position.x] = None
                                tile.locked = False
                                self.tiles[last_turn]["HAND"].append(tile)
                            self.tiles[last_turn]["PLAY"].clear()

                            # revoke last turn's score
                            self.scores[last_turn] -= self.play_score
                            self.play_score = 0

                            success = True
                    if not success:
                        self.change_turn()

                self.new_words.clear()

            elif key == KeyCode.from_char("4"): # change write direction
                self.direction = not self.direction

            elif key == Key.esc:
                # exit game
                if not self.standalone:
                    self.arcade.transition.draw()
                    self.arcade.status = Status.PRE_GAME
                    self.arcade.on_press(Key.up)
                else:
                    self.running = False

            if key != Key.esc:
                self.render()

        except AttributeError:
            pass

    def run_replay(self): ...

    def run(self):
        try:
            self.start()
            replay = (
                self.arcade.status != Status.IN_REPLAY if not self.standalone else False
            )
            if not replay:
                # if not self.standalone:
                #     self.arcade.game_info.data["CELLS"] += cells
                self.render()

            if self.standalone:
                from pynput import keyboard
                import os

                def on_key_press(key):
                    self.on_press(key)
                    if not self.running:
                        listener.stop()

                with keyboard.Listener(on_press=on_key_press) as listener:
                    listener.join()

                # os.system("cls" if os.name == "nt" else "clear")

        except KeyboardInterrupt:
            pass


# tiles toggle
# challenging mechanic

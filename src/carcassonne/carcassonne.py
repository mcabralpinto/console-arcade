from dataclasses import dataclass
from pynput.keyboard import Key, KeyCode
from typing import Any
import random
from copy import deepcopy

from game import Game
from utils import Status, Coordinate, load_data
from carcassonne.drawable import Board, UI
from carcassonne.utils import Tile, Player, Meeple, TileEdge, TileParts, StructureSet


@dataclass
class Carcassonne(Game):
    def start(self) -> None:
        # starting configurations
        self.fov = Coordinate(7, 5)
        self.n_players = 4
        self.display = {
            "BOARD": Board(
                dim=Coordinate(
                    (self.fov.x * 2 + 1) * 6,
                    (self.fov.y * 2 + 1) * 3,
                )
            ),
            "UI": UI(
                dim=Coordinate(self.n_players * 16 - 1, 3),
                offset=Coordinate(0, (self.fov.y + 1) * 3 + 2),
            ),
        }
        self.KEYS = {
            "MOVE": [Key.left, Key.right, Key.up, Key.down],
            "PAN": [
                KeyCode(char="a"),
                KeyCode(char="d"),
                KeyCode(char="w"),
                KeyCode(char="s"),
            ],
        }  # key mapping
        self.standalone = self.arcade is None
        self.running = True

        # initialize players
        self.players = [
            Player("PURPLE"),
            Player("B_PURPLE"),
            Player("BLUE"),
            Player("CYAN"),
        ][: self.n_players]

        # set the turn
        self.turn = -1

        # create tile set
        self.tiles = self.build_tiles(load_data("games\\carcassonne"))

        # initialize board
        self.board: dict[Coordinate, Tile] = {}
        self.bound = {"LOWER": Coordinate(-1, -1), "UPPER": Coordinate(1, 1)}
        self.board_shift = Coordinate(0, 0)
        self.structure_sets: list[StructureSet] = []

        # choose first tiles
        self.tile = self.tiles.pop(55)
        self.tile.position = Coordinate(0, 0)
        self.tile.locked = True
        self.board[self.tile.position] = deepcopy(self.tile)
        self.new_turn()

    def render(self) -> None:
        self.display["BOARD"].draw(
            [
                self.board,
                self.board_shift,
            ]
        )
        self.display["UI"].draw(
            [
                self.players,
            ]
        )

    def build_tiles(self, data: dict[str, Any]) -> list[Tile]:
        # create tile set from JSON data
        tiles = []
        for tile in data["TILES"]:
            for _ in range(tile["AMOUNT"]):
                tiles.append(
                    Tile.init(raw_structures=tile["STRUCTURES"], position=None)
                )
        return tiles

    def update_bounds(self):
        # update board bounds
        self.bound["LOWER"] = Coordinate(
            min(self.bound["LOWER"].x, self.tile.position.x - 1),
            min(self.bound["LOWER"].y, self.tile.position.y - 1),
        )
        self.bound["UPPER"] = Coordinate(
            max(self.bound["UPPER"].x, self.tile.position.x + 1),
            max(self.bound["UPPER"].y, self.tile.position.y + 1),
        )

    def update_structure_sets(self):
        for edge in self.tile.get_edges():
            for structure_set in self.structure_sets:
                for loose_edge in structure_set.loose_edges:
                    if edge.fits(loose_edge):
                        structure_set.loose_edges.remove(loose_edge)
                        
                        structure_set.tiles.append(self.tile)
                        break

    def new_turn(self):
        # choose new tile
        self.tile = self.tiles.pop(random.randint(0, len(self.tiles) - 1))
        self.tile.position = self.next_position(self.bound["LOWER"], Key.right)
        self.board[self.tile.position] = self.tile

        # update structure sets
        self.update_structure_sets()

        # update turn
        self.turn = (self.turn + 1) % self.n_players

    def next_position(self, position: Coordinate, key: KeyCode) -> Coordinate:
        LB, UB = self.bound["LOWER"], self.bound["UPPER"]
        shift = Coordinate(
            *{
                Key.left: (-1, 0),
                Key.right: (1, 0),
                Key.up: (0, -1),
                Key.down: (0, 1),
            }[key]
        )

        # try to find the new tile position based on the pressed movement key
        while True:
            # shift tile
            position += shift
            position.correct(LB, UB)

            # try next if the position is occupied
            if position in self.board:
                continue

            # check if any tile is adjacent
            if any(
                neighbor in self.board and self.board[neighbor] is not self.tile
                for neighbor in position.neighbors()
            ):
                break

        return position

    def check_play_validity(self) -> bool:
        # check if the tile has matching structures with its neighbors
        for neighbor in self.tile.position.neighbors():
            if neighbor in self.board and not self.tile.fits(self.board[neighbor]):
                return False

        return True

    def check_meeple_placeability(self):
        # create a visited map for superpositions, which look at the board as a grid
        # of structures rather than tiles
        xr = range((self.bound["LOWER"].x + 1) * 6, (self.bound["UPPER"].x) * 6)
        yr = range((self.bound["LOWER"].y + 1) * 6, (self.bound["UPPER"].y) * 6)
        visited = {Coordinate(x, y): False for x in xr for y in yr}

        # get the superposition of the meeple and mark it as visited
        position: Coordinate = self.tile.position * 6 + self.tile.meeple.position
        visited[position] = True

        # store the reference structure to later compare with the new positions
        reference = self.tile.meeple.structure

        # perform a flood-fill to find other meeples within the same structure
        queue = [position]
        while queue:
            # get a new position to check its neighbors
            position = queue.pop(0)
            for new_position in position.neighbors():
                # find the position of the tile on the board
                board_position = Coordinate(new_position.x // 6, new_position.y // 6)

                # check if the board position is valid
                if board_position not in self.board or visited[new_position]:
                    continue

                # mark the position as visited
                visited[new_position] = True

                # find the position of the structure on the tile
                tile_position = Coordinate(new_position.x % 6, new_position.y % 6)

                # check if the structure is the same as the reference
                if (
                    self.board[board_position]
                    .structures[tile_position.y][tile_position.x]
                    .same_type(reference)
                ):
                    # if so and there is already a meeple on it, placement is invalid
                    if (
                        self.board[board_position].meeple is not None
                        and self.board[board_position].meeple.position == tile_position
                    ):
                        return False

                    # else add the new position to the queue
                    queue.append(new_position)

                # else, we just move on to the next position

        # if the queue runs out of points to check, placement is valid
        return True

    def on_press(self, key: KeyCode) -> None:
        display = True
        try:
            if key in self.KEYS["PAN"]:
                # move the board - merely visual change
                new_board_shift = self.board_shift + Coordinate(
                    *{
                        KeyCode(char="a"): (1, 0),
                        KeyCode(char="d"): (-1, 0),
                        KeyCode(char="w"): (0, 1),
                        KeyCode(char="s"): (0, -1),
                    }[key]
                )
                if (
                    new_board_shift.x < self.fov.x + self.bound["UPPER"].x
                    and new_board_shift.x > -self.fov.x + self.bound["LOWER"].x
                    and new_board_shift.y < self.fov.y + self.bound["UPPER"].y
                    and new_board_shift.y > -self.fov.y + self.bound["LOWER"].y
                ):
                    self.board_shift = new_board_shift

            elif key in self.KEYS["MOVE"]:
                if not self.tile.locked:
                    # find the next position for the current piece
                    new_position = self.next_position(self.tile.position, key)

                    # change the tile position on the board
                    self.board[new_position] = self.board.pop(self.tile.position)
                    self.tile.position = new_position

                elif self.tile.meeple:
                    self.tile.meeple.move(key)

            elif isinstance(key, KeyCode) and key.char and key.char.lower() == "r":
                if not self.tile.meeple:
                    # rotate a tile
                    self.tile.rotate()

            elif key == Key.space:
                if not self.tile.locked:
                    # set a tile on a place if the placement is valid
                    if self.check_play_validity():
                        # save current tile in position
                        self.tile.locked = True
                        self.board[self.tile.position] = self.tile
                        self.update_bounds()

                elif not self.tile.meeple:
                    # create a meeple
                    self.tile.meeple = Meeple(
                        tile=self.tile,
                        color=self.players[self.turn].color,
                        position=Coordinate(2, 2),
                        structure=self.tile.structures[2][2],
                    )

                else:
                    # change to deepcopy! (?)
                    if self.check_meeple_placeability():
                        if self.players[self.turn].meeples > 0:
                            self.players[self.turn].meeples -= 1
                            self.new_turn()

            elif key == Key.esc:
                # exit game
                if not self.tile.locked:
                    if not self.standalone:
                        self.arcade.transition.draw()
                        self.arcade.status = Status.PRE_GAME
                        self.arcade.on_press(Key.up)
                    else:
                        self.running = False
                    display = False
                elif not self.tile.meeple:
                    self.new_turn()
                else:
                    self.tile.meeple = None

            if display:
                self.render()
                # print(self.tile.meeple.index if self.tile.meeple else None)

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


# add case where new tile cannot be added
# cool visual effect where cities become the colors of the players who win them

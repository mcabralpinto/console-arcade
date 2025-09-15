from dataclasses import dataclass, field

from utils import Coordinate


@dataclass
class Tile:
    letter: str
    value: int
    position: Coordinate = field(default_factory=lambda: Coordinate(-1, -1))
    locked: bool = False

    def used(self) -> bool:
        return self.position != (-1, -1)

    def __str__(self):
        return f"{self.letter} @ ({self.position.x}, {self.position.y})"

    def __repr__(self):
        return self.__str__()

    def has_neighbor(self, board: list["Tile"], locked=False):
        x, y = self.position
        neighbors = []
        if y > 0:
            neighbors.append(board[y - 1][x])
        if y < 14:
            neighbors.append(board[y + 1][x])
        if x > 0:
            neighbors.append(board[y][x - 1])
        if x < 14:
            neighbors.append(board[y][x + 1])
        if locked:
            return any(tile and tile.locked for tile in neighbors)
        else:
            return any(tile for tile in neighbors)

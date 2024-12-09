import pyxel

class Star:
    def __init__(self, color_index: int) -> None:
        self.color_index = color_index
        self.v = 0
        self.u = [0, 16, 32, 48, 64][color_index]

    def color(self) -> int:
        return self.color_index
    
    def draw(self, x, y) -> None:
        pyxel.blt(x, y, 0, self.u, self.v, 16, 16, 0)

    def __eq__(self, other):
        if isinstance(other, Star):
            return self.color_index == other.color_index
        return False


def get_star(color_index: int) -> Star:
    return Star(color_index)
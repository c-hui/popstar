import pyxel

class RefreshButton:
    def __init__(self):
        self.x = None
        self.y = None

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 48, 16, 16, 16)

    def is_touch(self) -> bool:
        if self.x is None or self.y is None:
            return False
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.x <= pyxel.mouse_x <= self.x + 16 and self.y <= pyxel.mouse_y <= self.y + 16:
                return True
            
        return False
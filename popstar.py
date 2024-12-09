import sys

import pyxel

from mode import ClassicMode
from text import Text, draw_title


class App:
    def __init__(self):
        pyxel.init(160, 288, title="popstar")
        pyxel.load("my_resource.pyxres")
        if "pyodide" not in sys.modules:
            pyxel.mouse(True)

        self.mode = None

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.mode:
            self.mode.update()
        else:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.mode = ClassicMode()

    def draw(self):
        if self.mode:
            self.mode.draw()
        else:
            pyxel.cls(0)
            draw_title(
                Text("POPSTAR", pyxel.COLOR_YELLOW),
                Text("- PRESS START -", pyxel.COLOR_WHITE),
            )


App()

import pyxel
from datetime import date

class Background:
    def update(self) -> None:
        pass

    def draw(self) -> None:
        pass


class StarBackground(Background):
    def __init__(self):
        self.stars = []
        self.num_stars = 100
        self.star_color_high = 12
        self.star_color_low = 5

        for i in range(self.num_stars):
            self.stars.append(
                (
                    pyxel.rndi(0, pyxel.width - 1),
                    pyxel.rndi(0, pyxel.height - 1),
                    pyxel.rndf(1, 2.5),
                )
            )

    def update(self):
        for i, (x, y, speed) in enumerate(self.stars):
            y += speed
            if y >= pyxel.height:
                y -= pyxel.height
            self.stars[i] = (x, y, speed)

    def draw(self):
        for x, y, speed in self.stars:
            pyxel.pset(
                x, y, self.star_color_high if speed > 1.8 else self.star_color_low
            )

class SnowBackground(Background):
    def __init__(self):
        self.stars = []
        self.num_stars = 20
        self.star_color_high = 12
        self.star_color_low = 5

        for i in range(self.num_stars):
            self.stars.append(
                (
                    pyxel.rndi(0, pyxel.width - 1),
                    pyxel.rndi(0, pyxel.height - 1),
                    pyxel.rndf(1, 2.5),
                )
            )

    def update(self):
        for i, (x, y, speed) in enumerate(self.stars):
            y += speed
            if y >= pyxel.height:
                y -= pyxel.height
            self.stars[i] = (x, y, speed)

    def draw(self):
        for x, y, speed in self.stars:
            # pyxel.pset(
            #     x, y, self.star_color_high if speed > 1.8 else self.star_color_low
            # )

            pyxel.blt(x, y, 0, 0, 48, 7, 7, 0)

def get_background() -> Background:
    if date.month in (12, 1, 2):
        return SnowBackground()
    else:
        return StarBackground()

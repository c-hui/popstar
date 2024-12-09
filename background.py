import pyxel


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


def get_background() -> Background:
    return StarBackground()

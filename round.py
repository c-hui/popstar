from button import RefreshButton
from star import get_star, Star
import pyxel
import random
from collections import OrderedDict
from music import (
    play_background_music,
    play_click_sound,
    play_gameover_music,
)
from text import Text, draw_header


class Round:
    def __init__(self) -> None:
        self.score = 0
        self.level = 0
        self.round_over = False
        self.game_over = False
        self.start()
        self.refresh_button = RefreshButton()

    def start(self) -> None:
        self.bonus_score = 0
        self.level += 1
        self.goal = 1000 + (self.level - 1) * 2000

        # 存放星星的网格
        self.grid: list[list[Star]] = []

        # 前 10 行不显示
        for _ in range(28):
            self.grid.append([None] * 10)

        # 生成 grid
        self.generate_grid()

        # 存放待消灭的星星
        self.clear_stars: dict[tuple[int, int], Star] = OrderedDict()

        self.round_over = False

    def generate_grid(self) -> list[list[Star]]:
        # 根据当前等级 生成 10x10 的网格
        grid = [[None for _ in range(10)] for _ in range(10)]

        # 随机颜色的概率 否则选择与相邻星星不同的颜色
        # 25 级达到最低的概率 0.1 游戏难度最高
        random_color_probability = max(0.1, 1.0 - self.level // 5 * 0.2)

        for row in range(10):
            for col in range(10):
                selected_color = None
                colors = [0, 1, 2, 3, 4]
                random.shuffle(colors)
                for color in colors:
                    # 随机决定是否检查相邻颜色
                    if random.random() < random_color_probability:
                        selected_color = color
                        break
                    else:
                        # 相邻颜色检查
                        if row > 0:
                            # 检查左上
                            if col > 0 and grid[row - 1][col - 1] == color:
                                continue
                            # 检查正上
                            if grid[row - 1][col] == color:
                                continue
                            # 检查右上
                            if col < 9 and grid[row - 1][col + 1] == color:
                                continue
                        # 检查左边
                        if col > 0 and grid[row][col - 1] == color:
                            continue
                        selected_color = color
                        break
                grid[row][col] = get_star(selected_color)

        for y in range(10):
            for x in range(10):
                self.grid[y][x] = grid[y][x]


    def is_over(self) -> bool:
        for x in range(0, 9):
            for y in range(1, 11):
                if self.grid[-y][x] is not None:
                    if self.grid[-y][x] == self.grid[-y - 1][x]:
                        return False
                    if self.grid[-y][x] == self.grid[-y][x + 1]:
                        return False
        return True

    def bonus(self):
        n = 0
        for col in self.grid:
            for star in col:
                if star is not None:
                    n += 1
        if n < 10:
            bonus = 2000 - n * n * 20

            self.score += bonus
            self.bonus_score = bonus

    def pop_star(self, x1, y1, x2, y2):
        if x2 < 0 or x2 > 9 or y2 < 0 or y2 > len(self.grid) - 1:
            return
        if self.grid[y1][x1] == self.grid[y2][x2]:
            if (x1, y1) not in self.clear_stars:
                self.clear_stars[(x1, y1)] = self.grid[y1][x1]
            if (x2, y2) not in self.clear_stars:
                self.clear_stars[(x2, y2)] = self.grid[y2][x2]
                self.pop(x2, y2)

    def pop(self, x, y):
        if self.grid[y][x] is None:
            return
        # 判断上下左右是否有相同颜色
        for x1, y1 in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if 0 <= x1 < 10 and 0 <= y1 < len(self.grid):
                self.pop_star(x, y, x1, y1)

    def update(self):
        # 需要消除
        if len(self.clear_stars) > 0:
            (x, y), star = self.clear_stars.popitem()
            self.grid[y][x] = None
            del star
            return

        # 下落和左移
        moved = False
        # 下落
        for x in range(10):
            last_y = None
            for y in range(len(self.grid) - 1, -1, -1):
                if self.grid[y][x] is None:
                    if last_y is None:
                        last_y = y
                else:
                    if last_y is not None:
                        new_y = pyxel.rndi(y + 1, last_y)
                        # 移动 y 处的星星到 new_y 处
                        self.grid[new_y][x] = self.grid[y][x]
                        self.grid[y][x] = None
                        moved = True
                        break
        # 整列左移
        for x in range(9):
            nums = 0
            for y in range(len(self.grid)):
                if self.grid[y][x] is not None:
                    nums += 1
            if nums > 0:
                continue
            for y in range(len(self.grid)):
                if self.grid[y][x + 1] is not None:
                    self.grid[y][x] = self.grid[y][x + 1]
                    self.grid[y][x + 1] = None
                    moved = True

        if moved:
            return

        # 判断该回合是否结束
        if self.is_over():
            self.bonus()
            if self.goal <= self.score:
                # 下一关
                self.round_over = True
                play_background_music()
                return
            else:
                # 游戏结束
                self.game_over = True
                play_gameover_music()
                return

        # 处理点击事件
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if (
                0 <= pyxel.mouse_x <= pyxel.width
                and pyxel.height - 160 <= pyxel.mouse_y <= pyxel.height
            ):
                x = pyxel.mouse_x // 16
                y = pyxel.mouse_y // 16 + 10
                self.pop(x, y)
                n = len(self.clear_stars)
                if n > 0:
                    play_click_sound()
                    self.score += 5 * n * n

        if self.refresh_button.is_touch():
            self.__init__()

    def draw(self):
        """draw 当前回合界面"""
        # 标题
        level_text = Text(f"LEVEL: {self.level}")
        goal_text = Text(f"GOAL: {self.goal}")
        score_text = Text(f"SCORE: {self.score}")
        if self.bonus_score > 0:
            bonus_text = Text("BONUS: %s" % self.bonus_score, pyxel.COLOR_YELLOW)
            h = draw_header(level_text, goal_text, score_text, bonus_text)
        else:
            h = draw_header(level_text, goal_text, score_text)
        
        self.refresh_button.y = h
        self.refresh_button.x = pyxel.width - 20

        self.draw_refresh_button(pyxel.width - 20, h)

        # 小星星
        for y in range(10, len(self.grid)):
            real_y = y * 16 - 10 * 16
            for x in range(10):
                if self.grid[y][x] is not None:
                    real_x = x * 16
                    self.grid[y][x].draw(real_x, real_y)

    def draw_refresh_button(self, x, y):
        pyxel.blt(x, y, 0, 48, 16, 16, 16)
import pyxel
import random
from collections import OrderedDict
from datetime import datetime
import sys
import os
import json

SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2
SCENE_CONTINUE = 3

COLOR_X = [0, 16, 32, 48, 64]

pwd = os.path.dirname(__file__)
config_path = os.path.join(pwd, ".config")


if "pyodide" in sys.modules:
    import js
else:
    js = None


def save_to_local_storage(key, value):
    if js:
        js.localStorage.setItem(key, value)
    else:
        if os.path.isfile(config_path):
            with open(config_path) as fin:
                config = json.loads(fin.read())
        else:
            config = {}
        config[key] = value
        with open(config_path, "w") as fout:
            fout.write(json.dumps(config))


def get_from_local_storage(key):
    if js:
        return js.localStorage.getItem(key)
    else:
        if os.path.isfile(config_path):
            with open(config_path) as fin:
                config = json.loads(fin.read())
                return config.get(key)
        else:
            return None

# 定义检查相邻星星颜色的函数，增加 difficulty 参数用于控制检查范围
def is_valid_color(grid, row, col, color, difficulty):
    # 检查上下左右的距离限制
    for dr in range(-difficulty, difficulty + 1):
        for dc in range(-difficulty, difficulty + 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < 10 and 0 <= nc < 10 and grid[nr][nc] == color:
                return False
    return True

# 检查颜色冲突时引入概率机制
def is_valid_color_with_probability(grid, row, col, color, difficulty, conflict_probability):
    # 随机决定是否允许冲突
    if random.random() < conflict_probability:
        return True  # 允许冲突
    
    # 检查相邻颜色是否不同
    return is_valid_color(grid, row, col, color, difficulty)

# 生成星星网格，增加 conflict_probability 参数来控制冲突概率
def generate_grid_with_conflict(grid, difficulty, conflict_probability):
    for row in range(10):
        for col in range(10):
            random.shuffle(COLOR_X)
            selected_color = None
            for color in COLOR_X:
                if is_valid_color_with_probability(grid, row, col, color, difficulty, conflict_probability):
                    selected_color = color
                    break
            
            # 填充该格子的颜色
            grid[row][col] = selected_color

# 根据关卡调整 conflict_probability 的值
def generate_level_with_conflict(level):
    grid = [[None for _ in range(10)] for _ in range(10)]
    # 难度随着关卡增加，检查范围逐步扩大
    difficulty = 1
    # 冲突概率逐渐减小，关卡越高，允许的冲突越少
    conflict_probability = max(0.1, 1.0 - level // 5 * 0.2)  # 随着关卡增加，冲突概率下降
    print(f"Level {level}, Difficulty {difficulty}, Conflict Probability {conflict_probability}")
    generate_grid_with_conflict(grid, difficulty, conflict_probability)
    return grid

class Round:
    def __init__(self) -> None:
        self.score = 0
        self.level = 0
        self.start()

    def start(self):
        self.bonus_score = 0
        self.level += 1

        self.page = []

        for _ in range(28):
            self.page.append([None] * 10)

        grid = generate_level_with_conflict(self.level)
        for y in range(10):
            for x in range(10):
                self.page[y][x] = grid[y][x]

        # 存放待消灭的星星
        self.clear_stars = OrderedDict()

    def goal(self) -> int:
        return 1000 + (self.level - 1) * 2000

    def is_over(self) -> bool:
        for x in range(0, 9):
            for y in range(1, 11):
                if self.page[-y][x] is not None:
                    if self.page[-y][x] == self.page[-y - 1][x]:
                        return False
                    if self.page[-y][x] == self.page[-y][x + 1]:
                        return False
        return True

    def pop_star(self, x1, y1, x2, y2):
        if self.page[y1][x1] == self.page[y2][x2]:
            if (x1, y1) not in self.clear_stars:
                self.clear_stars[(x1, y1)] = 0
            if (x2, y2) not in self.clear_stars:
                self.clear_stars[(x2, y2)] = 0
                self.pop(x2, y2)

    def pop(self, x, y):
        if self.page[y][x] is None:
            return

        if x - 1 >= 0:
            self.pop_star(x, y, x - 1, y)
        if x + 1 < 10:
            self.pop_star(x, y, x + 1, y)
        if y - 1 >= 0:
            self.pop_star(x, y, x, y - 1)
        if y + 1 < len(self.page):
            self.pop_star(x, y, x, y + 1)

    def bonus(self):
        n = 0
        for col in self.page:
            for star in col:
                if star is not None:
                    n += 1
        if n < 10:
            bonus = 2000 - n * n * 20

            self.score += bonus
            self.bonus_score = bonus

    def update(self):
        # 消除
        if len(self.clear_stars) > 0:
            (x, y), _ = self.clear_stars.popitem()
            self.page[y][x] = None
            return

        moved = False
        for x in range(10):
            last_y = None
            for y in range(len(self.page) - 1, -1, -1):
                if self.page[y][x] is None:
                    if last_y is None:
                        last_y = y
                else:
                    if last_y is not None:
                        new_y = pyxel.rndi(y + 1, last_y)
                        # 移动 y 处的星星到 new_y 处
                        self.page[new_y][x] = self.page[y][x]
                        self.page[y][x] = None
                        moved = True
                        break

        for x in range(9):
            nums = 0
            for y in range(len(self.page)):
                if self.page[y][x] is not None:
                    nums += 1
            if nums > 0:
                continue
            for y in range(len(self.page)):
                if self.page[y][x + 1] is not None:
                    self.page[y][x] = self.page[y][x + 1]
                    self.page[y][x + 1] = None
                    moved = True
        if moved:
            return

        # 判断是否结算
        if self.is_over():
            self.bonus()
            if self.goal() <= self.score:
                # 下一关
                if datetime(2024,11,4,0,0,0) <= datetime.now() <= datetime(2024,11,4,23,59,59):
                    pyxel.play(0, 3, loop=True)
                else:
                    pyxel.play(0, 0, loop=True)
                return SCENE_CONTINUE
            else:
                pyxel.play(0, 1)
                # 游戏结束
                return SCENE_GAMEOVER

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if (      0 <= pyxel.mouse_x <= pyxel.width
                and pyxel.height - 160 <= pyxel.mouse_y <= pyxel.height
            ):
                x = pyxel.mouse_x // 16
                y = pyxel.mouse_y // 16 + 10
                self.pop(x, y)
                n = len(self.clear_stars)
                if n > 0:
                    pyxel.play(0, 2)
                    self.score += 5 * n * n

    def draw(self):
        level_text = f"LEVEL: {self.level}"
        level_num = len(level_text)
        goal_text = f"GOAL: {self.goal()}"
        goal_num = len(goal_text)
        score_text = f"SCORE: {self.score}"
        score_num = len(score_text)
        x = pyxel.width - 4 * (level_num + goal_num + score_num + 4)
        x = x // 2
        pyxel.text(x, 6, level_text, 7)
        x += (level_num + 2) * 4
        pyxel.text(x, 6, goal_text, 7)
        x += (goal_num + 2) * 4
        pyxel.text(x, 6, score_text, 7)

        if self.bonus_score > 0:
            pyxel.text(60, 32, "BONUS: %s" % self.bonus_score, 10)

        for y in range(10, len(self.page)):
            real_y = y * 16 - 10 * 16
            for x in range(10):
                if self.page[y][x] is not None:
                    real_x = x * 16
                    pyxel.blt(real_x, real_y, 0, self.page[y][x], 0, 16, 16)


class Background:
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


class App:
    def __init__(self):
        # 加载记录
        self.max_score = 0
        self.record_date = 0
        max_score = get_from_local_storage("max_score")
        if max_score is not None:
            self.max_score = int(max_score)
        record_date = get_from_local_storage("record_date")
        if record_date is not None:
            self.record_date = record_date

        pyxel.init(160, 288, title="popstar")
        pyxel.load("my_resource.pyxres")
        if js is None:
            pyxel.mouse(True)

        self.scene = SCENE_TITLE

        self.background = Background()

        self.round = Round()

        # 小星星背景音乐
        pyxel.sounds[0].set(
            "c3c3g3g3a3a3g3 rf3f3e3e3d3d3c3 rg3g3f3f3e3e3d3 rg3g3f3f3e3e3d3 r"
            "c3c3g3g3a3a3g3 rf3f3e3e3d3d3c3 r",
            "t",  # 使用三角波音色
            "6",  # 音量设置
            "f",  # 无效果
            60,  # 节奏速度
        )

        # 创建游戏结束的音乐，使用简单的和弦
        pyxel.sounds[1].set(
            # 音符序列，创建平和的下降旋律
            "g2e2c2 g3r f3r e3r d3c3",
            "t",  # 使用三角波音色
            "6",  # 音量
            "f",  # 无效果
            20    # 设置较慢的节奏
        )

        # 设置更简单、更柔和的点击音效
        pyxel.sounds[2].set(
            "c4e4",  # 简短的C和E两个高音音符
            "t",     # 使用三角波音色，音色较柔和
            "6",     # 设置音量
            "f",     # 无特殊效果
            10       # 较快的节奏，保持清脆感
        )

        # 设置生日快乐的旋律
        pyxel.sounds[3].set(
            # 旋律音符
            "c4c4d4c4f4e4 r c4c4d4c4g4f4 r"
            "c4c4c4a4f4e4d4 r b3b3a4f4g4f4 r",
            "t",  # 使用三角波音色
            "6",  # 设置音量
            "f",  # 无效果
            50    # 设置适中的节奏
        )

        if datetime(2024,11,4,0,0,0) <= datetime.now() <= datetime(2024,11,4,23,59,59):
            pyxel.play(0, 3, loop=True)
        else:
            pyxel.play(0, 0, loop=True)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.background.update()

        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_PLAY:
            ret = self.update_play_scene()
            if ret is not None:
                self.scene = ret
            else:
                self.update_refresh_button()
        elif self.scene == SCENE_CONTINUE:
            self.update_continue_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.update_gameover_scane()

    def draw(self):
        pyxel.cls(0)
        self.background.draw()

        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
            self.draw_refresh_button()
        elif self.scene == SCENE_CONTINUE:
            self.draw_play_scene()
            self.draw_continue_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.draw_play_scene()
            self.draw_gameover_scene()

    def update_refresh_button(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if (
                pyxel.width - 20 <= pyxel.mouse_x <= pyxel.width - 4
                and 20 <= pyxel.mouse_y <= 36
            ):
                # 重新来过
                self.round = Round()

    def update_gameover_scane(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.round.score > self.max_score:
                self.max_score = self.round.score
                self.record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_to_local_storage("max_score", self.max_score)
                save_to_local_storage("record_date", self.record_date)

            self.round = Round()
            pyxel.stop()
            self.scene = SCENE_PLAY

    def update_continue_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.round.start()
            pyxel.stop()
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        return self.round.update()

    def update_title_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            pyxel.stop()
            self.scene = SCENE_PLAY

    def draw_refresh_button(self):
        pyxel.blt(pyxel.width - 20, 20, 0, 48, 16, 16, 16)

    def draw_gameover_scene(self):
        str_list = ["GAME OVER"]
        color_list = [pyxel.COLOR_RED]
        if self.max_score >= self.round.score:
            str_list.append(f"MAX SCORE: {self.max_score}")
            str_list.append(self.record_date)
            color_list.append(pyxel.COLOR_WHITE)
            color_list.append(pyxel.COLOR_WHITE)
        else:
            str_list.append("CONGRATULATION!")
            str_list.append(f"NEW RECORD: {self.round.score}")
            color_list.append(pyxel.COLOR_YELLOW)
            color_list.append(pyxel.COLOR_YELLOW)
        str_list.append("- PRESS RESTART -")
        color_list.append(pyxel.COLOR_WHITE)
        self.draw_title(str_list, color_list)

    def draw_continue_scene(self):
        self.draw_title(
            [
                "CONGRATULATION PASS",
                "HAPPY BIRTHDAY" if datetime(2024,11,4,0,0,0) <= datetime.now() <= datetime(2024,11,4,23,59,59) else "",
                "- PRESS CONTINUE -",
            ],
            [
                13,
                13,
                13,
            ],
        )

    def draw_play_scene(self):
        self.round.draw()

    def draw_title_scene(self):
        self.draw_title(
            [
                "HAPPY BIRTHDAY" if datetime(2024,11,4,0,0,0) <= datetime.now() <= datetime(2024,11,4,23,59,59) else "POPSTAR",
                "" if self.max_score == 0 else f"MAX SCORE: {self.max_score}",
                "" if self.max_score == 0 else f"{self.record_date}",
                "- PRESS START -",
            ],
            [
                lambda: pyxel.frame_count % 16,
                13,
                13,
                13,
            ],
        )

    def draw_title(self, text_list, color_list):
        n = len(text_list)
        y = (n * 2 + 1) * 6
        y = (pyxel.height - y) // 2
        for i, (text, color) in enumerate(zip(text_list, color_list)):
            if callable(color):
                color = color()
            x = (pyxel.width - len(text) * 4) // 2
            pyxel.text(x, y + i * 12, text, color)


App()

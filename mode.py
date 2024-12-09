import json
import os
from datetime import datetime

import pyxel

from background import get_background
from music import init_music, play_background_music
from round import Round
from text import Text, draw_title

CONF_FILENAME = "classic_mode.json"

vendor_name = "shichunhui"
app_name = "popstar"


def get_from_local_storage(key) -> str:
    storage_path = pyxel.user_data_dir(vendor_name, app_name)
    conf_path = os.path.join(storage_path, CONF_FILENAME)
    if not os.path.exists(conf_path):
        return None
    with open(conf_path, "r") as f:
        data = json.load(f)
        return data.get(key)


def save_to_local_storage(key, value):
    storage_path = pyxel.user_data_dir(vendor_name, app_name)
    conf_path = os.path.join(storage_path, CONF_FILENAME)
    if os.path.exists(conf_path):
        with open(conf_path, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[key] = value
    with open(conf_path, "w") as f:
        json.dump(data, f)


class ClassicMode:
    def __init__(self) -> None:
        # 加载记录
        self.max_score = 0
        self.record_date = 0
        max_score = get_from_local_storage("max_score")
        if max_score is not None:
            self.max_score = int(max_score)
        record_date = get_from_local_storage("record_date")
        if record_date is not None:
            self.record_date = record_date

        self.background = get_background()

        self.round = Round()

        init_music()

        play_background_music()

    def update(self):
        self.background.update()

        if self.round.game_over:
            self.update_gameover_scane()
        elif self.round.round_over:
            self.update_continue_scene()
        else:
            self.round.update()

    def update_gameover_scane(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.round.score > self.max_score:
                self.max_score = self.round.score
                self.record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_to_local_storage("max_score", self.max_score)
                save_to_local_storage("record_date", self.record_date)

            self.round = Round()
            pyxel.stop()

    def update_continue_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.round.start()
            pyxel.stop()

    def draw(self):
        pyxel.cls(0)
        self.background.draw()

        if self.round.game_over:
            self.draw_gameover_scene()
        elif self.round.round_over:
            self.draw_continue_scene()
        self.round.draw()

    def draw_gameover_scene(self):
        text_list = [Text("GAME OVER", pyxel.COLOR_RED)]

        if self.max_score > self.round.score:
            text_list.append(Text(f"MAX SCORE: {self.max_score}", pyxel.COLOR_WHITE))
            text_list.append(Text(self.record_date, pyxel.COLOR_WHITE))
        else:
            text_list.append(Text("CONGRATULATION!", pyxel.COLOR_YELLOW))
            text_list.append(
                Text(f"NEW RECORD: {self.round.score}", pyxel.COLOR_YELLOW)
            )

        text_list.append(Text("- PRESS RESTART -", pyxel.COLOR_WHITE))

        draw_title(*text_list)

    def draw_continue_scene(self):
        draw_title(
            Text("CONGRATULATION PASS", pyxel.COLOR_YELLOW),
            Text("- PRESS CONTINUE -", pyxel.COLOR_WHITE),
        )

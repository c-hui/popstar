import pyxel
from datetime import datetime


def init_music() -> None:
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
        20,  # 设置较慢的节奏
    )
    # 设置更简单、更柔和的点击音效
    pyxel.sounds[2].set(
        "c4e4",  # 简短的C和E两个高音音符
        "t",  # 使用三角波音色，音色较柔和
        "6",  # 设置音量
        "f",  # 无特殊效果
        10,  # 较快的节奏，保持清脆感
    )
    # 设置生日快乐的旋律
    pyxel.sounds[3].set(
        # 旋律音符
        "c4c4d4c4f4e4 r c4c4d4c4g4f4 r" "c4c4c4a4f4e4d4 r b3b3a4f4g4f4 r",
        "t",  # 使用三角波音色
        "6",  # 设置音量
        "f",  # 无效果
        50,  # 设置适中的节奏
    )


# 播放小星星音乐
def play_star_music():
    pyxel.play(0, 0, loop=True)


# 播放游戏结束音乐
def play_gameover_music():
    pyxel.play(0, 1)


# 播放点击音效
def play_click_sound():
    pyxel.play(0, 2)


# 播放生日快乐音乐
def play_birthday_music():
    pyxel.play(0, 3, loop=True)


# 播放背景音乐
def play_background_music():
    if (
        datetime(2024, 11, 4, 0, 0, 0)
        <= datetime.now()
        <= datetime(2024, 11, 4, 23, 59, 59)
    ):
        play_birthday_music()
    else:
        play_star_music()

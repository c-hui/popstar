import pyxel

class Text:
    def __init__(self, content: str, color: int = pyxel.COLOR_WHITE):
        self.content = content
        self.color = color
        self.x = 0
        self.y = 0

    def draw(self):
        pyxel.text(self.x, self.y, self.content, self.color)

def draw_header(*texts: Text):
    # 画面顶层显示文本
    # 一个字符水平方向占4个像素 垂直方向占6个像素
    # 水平方向每个字符串等间隔分布 最少间隔要大于 2 个像素
    # 否则不断尝试将后面的字符串挪到下一行显示
    total_num = len(texts)
    text_size_list = [len(text.content) for text in texts]

    multi_text: list[list[Text]] = []
    line_text: list[Text] = []
    line_size = 2
    for i in range(total_num):
        line_size += text_size_list[i] * 4 + 2
        if line_size > pyxel.width:
            multi_text.append(line_text)
            line_text = []
            line_size = 2 + text_size_list[i] * 4 + 2
        line_text.append(texts[i])
    else:
        multi_text.append(line_text)

    h = 6

    for line_text in multi_text:
        n = len(line_text)
        text_char_length = sum([len(text.content) for text in line_text])
        space = (pyxel.width - text_char_length * 4) // (n + 1)
        x = 0
        for text in line_text:
            text.x = x + space
            text.y = h
            text.draw()
            x = text.x + len(text.content) * 4
        h += 12

    return h

def draw_title(*texts: Text):
    # 画面中央显示文本
    # 一个字符水平方向占4个像素 垂直方向占6个像素
    # 垂直方向均匀排列每个字符串，每个字符串间隔6个像素，水平方向居中排列
    total_num = len(texts)
    y = (total_num * 2 + 1) * 6
    y = (pyxel.height - y) // 2
    for text in texts:
        text.x = (pyxel.width - len(text.content) * 4) // 2
        text.y = y
        text.draw()
        y += 12

if __name__ == "__main__":
    pyxel.init(256, 256)
    pyxel.cls(0)
    draw_title(
        Text("Hello", pyxel.COLOR_RED),
        Text("World", pyxel.COLOR_GREEN),
        Text("This is a long text"),
        Text("This is a long text"),
        Text("This is a long text"),
        Text("This is a long text"),
        Text("This is a long text"),
        Text("This is a long text"),
    )
    pyxel.show()
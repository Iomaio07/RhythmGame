import arcade


class ComboText:

    def __init__(self, text, x, y):
        self.text = str(text)
        self.x = x
        self.y = y
        self.lifetime = 1  # Время отображения в секундах
        self.alpha = 255
        self.font_size = 36
        self.color = arcade.color.GRAY
        self.text_obj = arcade.Text(self.text, self.x, self.y, self.color, self.font_size, anchor_x="center", bold=True)

    def update(self, delta_time):
        self.lifetime -= delta_time
        if self.lifetime > 0:
            self.alpha = int(255 * (self.lifetime / 1.0))
            self.y += 20 * delta_time
            self.text_obj.y = self.y
            self.text_obj.color = (self.color[0], self.color[1], self.color[2], self.alpha)

            return True
        return False

    def draw(self):
        if self.lifetime > 0:
            self.text_obj.draw()

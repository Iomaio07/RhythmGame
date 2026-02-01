import arcade
import arcade.gui
import os

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800


class ResultsView(arcade.View):
    def __init__(self, score, combo, full_combo, stats):
        super().__init__()
        self.score = score
        self.combo = combo
        self.full_combo = full_combo
        self.stats = stats

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        total_notes = sum(stats.values())
        self.accuracy = (stats['perfect'] * 100 + stats['great'] * 90 + stats['good'] * 70 + stats[
            'bad'] * 40) / total_notes

        self.grade = self.calculate_grade()

        self.write_results()

        # Текст
        self.results = arcade.Text("РЕЗУЛЬТАТЫ",
                                   SCREEN_WIDTH // 2,
                                   SCREEN_HEIGHT - 100,
                                   arcade.color.GOLD,
                                   50,
                                   bold=True,
                                   anchor_x="center")

        self.grade_text = arcade.Text(self.grade,
                                      SCREEN_WIDTH // 2,
                                      SCREEN_HEIGHT - 200,
                                      arcade.color.GOLD if self.grade in ["SS", "S"] else arcade.color.WHITE,
                                      100,
                                      bold=True,
                                      anchor_x="center")

        y_offset = SCREEN_HEIGHT - 350
        self.score_text = arcade.Text(f"Счет: {self.score}",
                                      100, y_offset, arcade.color.WHITE, 30)

        self.accuracy_text = arcade.Text(f"Точность: {self.accuracy:.2f}%",
                                         100, y_offset - 50, arcade.color.WHITE, 30)

        self.max_combo = arcade.Text(f"Максимальное комбо: {self.combo}/{self.full_combo}",
                                     100, y_offset - 100, arcade.color.WHITE, 30)

        stats_y = SCREEN_HEIGHT - 450

        self.perfect = arcade.Text(f"PERFECT: {self.stats['perfect']}",
                                   150, stats_y - 40, arcade.color.GOLD, 20)

        self.great = arcade.Text(f"GREAT: {self.stats['great']}",
                                 150, stats_y - 70, arcade.color.CYAN, 20)

        self.good = arcade.Text(f"GOOD: {self.stats['good']}",
                                150, stats_y - 100, arcade.color.BLUE_SAPPHIRE, 20)

        self.bad = arcade.Text(f"BAD: {self.stats['bad']}",
                               150, stats_y - 130, arcade.color.ORANGE, 20)

        self.miss = arcade.Text(f"MISS: {self.stats['miss']}",
                                150, stats_y - 160, arcade.color.GRAY, 20)

        self.create_exit_button()

    def create_exit_button(self):
        exit_button = arcade.gui.UIFlatButton(
            text="Выход",
            width=200,
            height=50
        )

        @exit_button.event("on_click")
        def on_click_exit_button(event):
            arcade.exit()

        h_box = arcade.gui.UIBoxLayout(vertical=False)
        h_box.add(exit_button)

        v_box = arcade.gui.UIBoxLayout()
        v_box.add(arcade.gui.UIWidget(height=SCREEN_HEIGHT - 600))
        v_box.add(h_box)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=v_box, anchor_x="center_x", anchor_y="bottom")
        self.manager.add(anchor)

    def calculate_grade(self):
        """Вычисляет оценку"""

        if self.accuracy >= 95:
            return "PERFECT"
        elif self.accuracy >= 90:
            return "EXCELLENT"
        elif self.accuracy >= 80:
            return "GREAT"
        elif self.accuracy >= 65:
            return "GOOD"
        elif self.accuracy >= 50:
            return "BAD"
        else:
            return "LOSS"

    def write_results(self):
        results_to_save = {
            'score': str(self.score),
            'max_combo': str(self.combo),
            'grade': str(self.grade),
            'perfect': str(self.stats['perfect']),
            'great': str(self.stats['great']),
            'good': str(self.stats['good']),
            'bad': str(self.stats['bad']),
            'miss': str(self.stats['miss'])
        }

        counter = 1
        while os.path.exists(f'results/results_{counter}.txt'):
            counter += 1

        with open(f'results/results_{counter}.txt', 'w', encoding='utf-8') as f:
            for key, value in results_to_save.items():
                f.write(f"{key}={value}\n")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.results.draw()
        self.grade_text.draw()
        self.score_text.draw()
        self.accuracy_text.draw()
        self.max_combo.draw()
        self.perfect.draw()
        self.great.draw()
        self.good.draw()
        self.bad.draw()
        self.miss.draw()

        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.ENTER or key == arcade.key.SPACE:
            arcade.close_window()

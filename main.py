import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout
import arcade

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = 'God Rhythms You'
Y_FOR_BUTTON = 100
Y_FOR_GODLY_BUTTON = 300
RADIUS = 40
GODLY_COEFF = 2
PERF_COEFF = 2
GREAT_COEFF = 1.5
GOOD_COEFF = 1
BAD_COEFF = 0.5
MISS_COEFF = 0
START_GAME = False
curr_time = 0
curr_song = ''


# --- Секция Arcade ---
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.notes_list = arcade.SpriteList()
        self.godly_notes_list = arcade.SpriteList()
        self.buttons_list = arcade.SpriteList()
        self.godly_buttons_list = arcade.SpriteList()
        self.score = 0
        self.setup()
        self.notes_from_txt(curr_song)

    def notes_from_txt(self, song_name):
        '''Подготавливает все ноты из txt.'''
        # Порядок - тип ноты, время, ряд
        with open(f'songs/{song_name}.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            data = []
            for _ in lines:
                data.append(_.split())
            for elem in data:
                if elem[0].lower() == 'demon':
                    sprite = 'img/DemonNote.jpg'
                    self.note = Note(sprite, 0.5, int(elem[1]), int(elem[2]), elem[0])
                    self.godly_notes_list.append(self.note)
                elif elem[0].lower() == 'godly':
                    sprite = 'img/GodlyNote.jpg'
                    self.note = Note(sprite, 0.5, int(elem[1]), int(elem[2]), elem[0])
                    self.godly_notes_list.append(self.note)
                else:
                    sprite = 'img/Note.jpg'
                    self.note = Note(sprite, 0.5, int(elem[1]), int(elem[2]), elem[0])
                    self.notes_list.append(self.note)

    def setup(self):
        self.button1 = Button('img/Button.png', 0.5, arcade.key.LEFT)
        self.button1.center_x = 150
        self.godly_button1 = Button('img/Button.png', 0.5, arcade.key.A, type='Godly')
        self.godly_button1.center_x = 150

        self.buttons_list.append(self.button1)
        self.godly_buttons_list.append(self.godly_button1)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        self.buttons_list.draw()
        self.godly_buttons_list.draw()
        self.notes_list.draw()
        self.godly_notes_list.draw()

    def on_update(self, delta_time):
        global curr_time
        self.notes_list.update()
        self.godly_notes_list.update()
        curr_time += delta_time

    def on_key_press(self, key, modifiers):
        for button in self.buttons_list:
            if key == button.key:
                self.check_collisions(button, self.notes_list, False)

        for button in self.godly_buttons_list:
            if key == button.key:
                self.check_collisions(button, self.godly_notes_list, True)

    def check_collisions(self, button, notes_list, is_godly):
        notes_hit_list = arcade.check_for_collision_with_list(button, notes_list)

        if not notes_hit_list:
            return

        closest_note = min(notes_hit_list,
                           key=lambda note: abs(note.center_y - button.center_y))

        distance = abs(closest_note.center_y - button.center_y)
        if distance <= 10:
            accuracy = "PERFECT"
            score_mult = PERF_COEFF
        elif distance <= 15:
            accuracy = "GREAT"
            score_mult = GREAT_COEFF
        elif distance <= 20:
            accuracy = "GOOD"
            score_mult = GOOD_COEFF
        elif distance <= 50:
            accuracy = "BAD"
            score_mult = BAD_COEFF
        else:
            accuracy = "MISS"
            score_mult = MISS_COEFF

        print(accuracy)
        base_score = 100
        if is_godly:
            base_score *= GODLY_COEFF
        self.score += int(base_score * score_mult)

        if closest_note.type.lower() == 'demon':
            new_note = Note('img/Note.jpg', 0.5, 0,
                            closest_note.row, 'normal')
            new_note.center_x = closest_note.center_x
            new_note.center_y = closest_note.center_y
            self.notes_list.append(new_note)

        closest_note.remove_from_sprite_lists()


class Note(arcade.Sprite):
    def __init__(self, filename, scale, time, row, type='normal'):
        global curr_time
        super().__init__(filename, scale)
        self.type = type
        self.row = row
        self.radius = RADIUS
        self.speed_y = 200
        self.time = time
        # для тестов
        self.center_x = 150
        if type == 'normal':
            self.center_y = Y_FOR_BUTTON + self.speed_y * self.time
        else:
            self.center_y = Y_FOR_GODLY_BUTTON + self.speed_y * self.time

    def update(self, delta_time):
        self.center_y -= self.speed_y * delta_time
        self.time_to_button = self.time - curr_time


class Button(arcade.Sprite):
    def __init__(self, filename, scale, key, type='normal'):
        super().__init__(filename, scale)
        self.type = type
        self.radius = RADIUS
        self.is_clicked = False
        self.key = key
        if type == 'normal':
            self.center_y = Y_FOR_BUTTON
        else:
            self.center_y = Y_FOR_GODLY_BUTTON


# --- Секция PyQt6 ---
class StartMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()

        self.mainmenu = MainMenu()
        self.selectsong = SelectSong()
        self.settings = Settings()

        self.stacked_widget.addWidget(self.mainmenu)
        self.stacked_widget.addWidget(self.selectsong)
        self.stacked_widget.addWidget(self.settings)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.stacked_widget.setCurrentIndex(0)

        self.mainmenu.btn_levels.clicked.connect(lambda: self.switch_page(1))
        self.mainmenu.btn_settings.clicked.connect(lambda: self.switch_page(2))

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/StartMenu.ui', self)
        self.setWindowTitle(SCREEN_TITLE)
        self.setFixedSize(720, 600)
        self.btn_exit.clicked.connect(self.exit)

    def exit(self):
        self.window().close()


class SelectSong(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/SelectSong.ui', self)
        self.setWindowTitle('Select Song')
        self.setFixedSize(800, 700)
        self.btn_song_4nim0sity.clicked.connect(lambda: self.start_game('4nim0sity'))
        self.btn_song_telepathy.clicked.connect(lambda: self.start_game('telepathy'))

    def start_game(self, song):
        global START_GAME, curr_song
        START_GAME = True
        curr_song = song
        self.window().close()


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/Settings.ui', self)
        self.setWindowTitle('Settings')
        self.setFixedSize(800, 700)
        self.volume = self.SliderVolume.value()
        self.tempvolume = self.volume
        self.FPS = self.lineEdit_FPS.text()
        self.tempFPS = self.FPS
        self.lineEdit_FPS.textChanged.connect(self.change_FPS)
        self.SliderVolume.valueChanged.connect(self.change_volume)
        self.btn_save.clicked.connect(self.save_changes)

    def change_volume(self):
        self.tempvolume = self.SliderVolume.value()
        self.LabelVolume.setText(f"{self.tempvolume}%")

    def change_FPS(self):
        self.tempFPS = self.lineEdit_FPS.text()

    def save_changes(self):
        self.FPS = self.tempFPS
        self.volume = self.tempvolume


def main():
    app = QApplication(sys.argv)
    menu = StartMenu()
    menu.show()
    app.exec()

    del app

    if START_GAME:
        window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        game_view = GameView()
        window.show_view(game_view)
        arcade.run()


if __name__ == '__main__':
    main()

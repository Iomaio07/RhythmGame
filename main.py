import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QMessageBox
import arcade
from ConfigManager import ConfigManager

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
buttons_lst = [arcade.key.LEFT, arcade.key.DOWN, arcade.key.UP, arcade.key.RIGHT]
godly_buttons_lst = [arcade.key.A, arcade.key.S, arcade.key.W, arcade.key.D]
master_volume = 1
music_volume = 1
sfx_volume = 1
fps = 60


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
        music = arcade.load_sound(f'sounds/{curr_song}.mp3')
        arcade.play_sound(music, volume=master_volume * music_volume)
        self.hit_sound = arcade.load_sound('sounds/hit_sound.mp3')


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
        for i in range(4):
            self.button1 = Button('img/Btn_left.png', 0.5, buttons_lst[i], i + 1)
            self.godly_button1 = Button('img/Button.png', 0.5, godly_buttons_lst[i], i + 1, type='Godly')

            self.buttons_list.append(self.button1)
            self.godly_buttons_list.append(self.godly_button1)

            self.score_text = arcade.Text('0', 900, 750, arcade.color.WHITE, 24, anchor_x="center")

            self.timer = 0
            self.normal_size = 30
            self.max_size = 40
            self.target_size = self.normal_size

    def on_show_view(self):
            arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        self.buttons_list.draw()
        self.godly_buttons_list.draw()
        self.notes_list.draw()
        self.godly_notes_list.draw()
        self.score_text.draw()

    def on_update(self, delta_time):
        global curr_time
        self.notes_list.update()
        self.godly_notes_list.update()
        curr_time += delta_time

        if self.timer > 0:
            self.timer -= delta_time
            if self.timer <= 0:
                self.target_size = self.normal_size

        dist = self.target_size - self.score_text.font_size

        if abs(dist) > 0.1:
            self.score_text.font_size += dist * 0.15
        else:
            self.score_text.font_size = self.target_size

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
        arcade.play_sound(self.hit_sound, volume=master_volume * sfx_volume)
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
        self.score += int(base_score * score_mult) + int(self.score_text.text)
        self.score_text.text = self.score
        self.target_size = self.max_size
        self.timer = 0.15

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
        self.radius = RADIUS
        self.speed_y = 400
        self.time = time
        self.row = row
        self.center_x = 200 * self.row
        if type == 'normal':
            self.center_y = Y_FOR_BUTTON + self.speed_y * self.time
        else:
            self.center_y = Y_FOR_GODLY_BUTTON + self.speed_y * self.time

    def update(self, delta_time):
        self.center_y -= self.speed_y * delta_time
        self.time_to_button = self.time - curr_time


class Button(arcade.Sprite):
    def __init__(self, filename, scale, key, row, type='normal'):
        super().__init__(filename, scale)
        self.type = type
        self.radius = RADIUS
        self.is_clicked = False
        self.key = key
        self.center_x = 200 * row
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
        self.selectsong.btn_back.clicked.connect(lambda: self.switch_page(0))
        self.settings.btn_back.clicked.connect(lambda: self.switch_page(0))

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

        self.cfg_mng = ConfigManager()

        saved_settings = self.cfg_mng.load_settings_to_vars()

        self.SliderMasterVolume.setValue(saved_settings['master_volume'])
        self.SliderMusicVolume.setValue(saved_settings['music_volume'])
        self.SliderSFXVolume.setValue(saved_settings['sfx_volume'])
        self.lineEdit_FPS.setText(str(saved_settings['fps']))

        self.master_volume = self.SliderMasterVolume.value()
        self.music_volume = self.SliderMusicVolume.value()
        self.sfx_volume = self.SliderSFXVolume.value()
        self.FPS = self.lineEdit_FPS.text()

        self.tempmastervolume = self.master_volume
        self.tempmusicvolume = self.music_volume
        self.tempsfxvolume = self.sfx_volume
        self.tempFPS = self.FPS

        self.Master_Volume.setText(f"{self.master_volume}%")
        self.Music_Volume.setText(f"{self.music_volume}%")
        self.SFX_Volume.setText(f"{self.sfx_volume}%")

        self.lineEdit_FPS.textChanged.connect(self.change_FPS)
        self.SliderMasterVolume.valueChanged.connect(self.change_master_volume)
        self.SliderMusicVolume.valueChanged.connect(self.change_music_volume)
        self.SliderSFXVolume.valueChanged.connect(self.change_sfx_volume)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_reset_defaults.clicked.connect(self.reset_to_defaults)

    def change_master_volume(self):
        self.tempmastervolume = self.SliderMasterVolume.value()
        self.Master_Volume.setText(f"{self.tempmastervolume}%")

    def change_music_volume(self):
        self.tempmusicvolume = self.SliderMusicVolume.value()
        self.Music_Volume.setText(f"{self.tempmusicvolume}%")


    def change_sfx_volume(self):
        self.tempsfxvolume = self.SliderSFXVolume.value()
        self.SFX_Volume.setText(f"{self.tempsfxvolume}%")


    def change_FPS(self):
        self.tempFPS = self.lineEdit_FPS.text()

    def save_changes(self):
        global master_volume, music_volume, sfx_volume, fps
        self.FPS = self.tempFPS
        self.master_volume = self.tempmastervolume
        self.music_volume = self.tempmusicvolume
        self.sfx_volume = self.tempsfxvolume
        master_volume = self.master_volume / 100
        music_volume = self.music_volume / 100
        sfx_volume = self.sfx_volume / 100
        fps = self.FPS

        config_to_save = {
            'master_volume': str(self.master_volume),
            'music_volume': str(self.music_volume),
            'sfx_volume': str(self.sfx_volume),
            'fps': str(self.FPS)
        }

        with open('config.txt', 'w', encoding='utf-8') as f:
            for key, value in config_to_save.items():
                f.write(f"{key}={value}\n")

    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите сбросить настройки к значениям по умолчанию?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.SliderMasterVolume.setValue(100)
            self.SliderMusicVolume.setValue(100)
            self.SliderSFXVolume.setValue(100)
            self.lineEdit_FPS.setText("60")

            self.tempmastervolume = 100
            self.tempmusicvolume = 100
            self.tempsfxvolume = 100
            self.tempFPS = "60"

            self.Master_Volume.setText("100%")
            self.Music_Volume.setText("100%")
            self.SFX_Volume.setText("100%")


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

import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QMessageBox
import arcade
from arcade.particles import FadeParticle, Emitter, EmitBurst
from ConfigManager import ConfigManager
from Accuracity import AccuracyText
from Combo import ComboText
from Results import ResultsView
from effects import gravity_drag
import time
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = 'God Rhythms You'
Y_FOR_BUTTON = 100
Y_FOR_GODLY_BUTTON = 300
NOTE_SPEED = 600
GODLY_COEFF = 1.5
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
btn_texture_lst = ['img/Btn_left.png', 'img/Btn_down.png', 'img/Btn_up.png', 'img/Btn_right.png']
godly_btn_texture_lst = ['img/Btn_a.png', 'img/Btn_s.png', 'img/Btn_w.png', 'img/Btn_d.png']
cfg_mng = ConfigManager()
saved_settings = cfg_mng.load_settings_to_vars()
master_volume = saved_settings['master_volume'] / 100
music_volume = saved_settings['music_volume'] / 100
sfx_volume = saved_settings['sfx_volume'] / 100
fps = int(saved_settings['fps'])


# --- Секция Arcade ---
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.notes_list = arcade.SpriteList()
        self.godly_notes_list = arcade.SpriteList()
        self.buttons_list = arcade.SpriteList()
        self.godly_buttons_list = arcade.SpriteList()
        self.slider_ends = arcade.SpriteList()
        self.gif_sprites = arcade.SpriteList()
        self.slider_bodies = []
        self.held_notes = []
        self.setup()
        self.notes_from_txt(curr_song)
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.full_combo = len(self.notes_list) + len(self.godly_notes_list)
        self.game_completed = False
        self.stats = {'miss': 0, 'bad': 0, 'good': 0, 'great': 0, 'perfect': 0}
        music = arcade.load_sound(f'sounds/{curr_song}.mp3')
        self.player = arcade.play_sound(music, volume=master_volume * music_volume)
        self.hit_sound = arcade.load_sound('sounds/hit_sound.mp3')

        self.accuracy_texts = []
        self.accuracy_colors = {
            "PERFECT": arcade.color.GOLD,
            "GREAT": arcade.color.CYAN,
            "GOOD": arcade.color.BLUE_SAPPHIRE,
            "BAD": arcade.color.ORANGE,
            "MISS": arcade.color.GRAY
        }
        self.animation_timer = 0
        self.animation_interval = 1 / 60
        self.combo_texts = []
        self.emitters = []

        self.start_time = time.perf_counter()

    def notes_from_txt(self, song_name):
        '''Подготавливает все ноты из txt.'''
        self.gif_sprite = arcade.load_animated_gif(f"img/{song_name}.gif")
        self.gif_sprite.center_x = 50
        self.gif_sprite.center_y = 750
        self.gif_sprite.scale = 0.2
        self.gif_sprites.append(self.gif_sprite)
        with open(f'songs/{song_name}.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            data = []
            for _ in lines:
                data.append(_.split())
            for elem in data:
                note_type = elem[0].lower()
                time = float(elem[1])
                row = int(elem[2])
                if len(elem) == 4:
                    duration = float(elem[3])
                    if note_type == 's':
                        sprite = 'img/SliderStart.png'
                        note = Note(sprite, 0.5, time, row, 'normal', duration)
                        self.notes_list.append(note)

                        slider_end = SliderEnd('img/SliderEnd.png', 0.5, time + duration, row, note)
                        self.slider_ends.append(slider_end)

                        slider_body = SliderBody(note, slider_end)
                        self.slider_bodies.append(slider_body)

                    elif note_type == 'gs':
                        sprite = 'img/GodlySliderStart.png'
                        note = Note(sprite, 0.5, time, row, 'godly', duration)
                        self.godly_notes_list.append(note)

                        slider_end = SliderEnd('img/GodlySliderEnd.png', 0.5, time + duration, row, note)
                        self.slider_ends.append(slider_end)

                        slider_body = SliderBody(note, slider_end)
                        self.slider_bodies.append(slider_body)
                else:
                    if note_type == 'd':
                        sprite = 'img/DemonNote.png'
                        note = Note(sprite, 0.5, time, row, 'demon')
                        self.godly_notes_list.append(note)
                    elif note_type == 'g':
                        sprite = 'img/GodlyNote.png'
                        note = Note(sprite, 0.5, time, row, 'godly')
                        self.godly_notes_list.append(note)
                    else:
                        sprite = 'img/Note.png'
                        note = Note(sprite, 0.5, time, row, 'normal')
                        self.notes_list.append(note)

    def setup(self):
        for i in range(4):
            self.button1 = Button(btn_texture_lst[i], 0.5, buttons_lst[i], i + 1)
            self.godly_button1 = Button(godly_btn_texture_lst[i], 0.5, godly_buttons_lst[i], i + 1, type='Godly')

            self.buttons_list.append(self.button1)
            self.godly_buttons_list.append(self.godly_button1)

            self.score_text = arcade.Text('0', 900, 750, arcade.color.WHITE, 24, anchor_x="center")

            self.timer = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        self.buttons_list.draw()
        self.godly_buttons_list.draw()

        for slider_body in self.slider_bodies:
            slider_body.draw()

        self.notes_list.draw()
        self.godly_notes_list.draw()
        self.slider_ends.draw()
        self.score_text.draw()

        for text in self.accuracy_texts:
            text.draw()

        for combo in self.combo_texts:
            combo.draw()

        for emitter in self.emitters:
            emitter.draw()

        self.gif_sprites.draw()

    def on_update(self, delta_time=1 / fps):
        global curr_time
        self.notes_list.update()
        self.godly_notes_list.update()
        self.check_missed_notes()
        self.slider_ends.update()
        self.gif_sprites.update()

        if self.combo > self.max_combo:
            self.max_combo = self.combo

        if not self.game_completed:
            total_notes_left = (len(self.notes_list) +
                                len(self.godly_notes_list) +
                                len(self.slider_ends))

            if total_notes_left == 0:
                self.game_completed = True
                self.show_results_delay = 1.0
            else:
                self.show_results_delay = None

        if self.show_results_delay is not None:
            self.show_results_delay -= delta_time
            if self.show_results_delay <= 0:
                results_view = ResultsView(self.score, self.max_combo, self.full_combo, self.stats, curr_song,
                                           self.player)
                self.window.show_view(results_view)
                return

        for slider_body in self.slider_bodies:
            slider_body.update()

            if slider_body.is_held:
                score_to_add = slider_body.update_hold_score()
                if score_to_add > 0:
                    self.score += score_to_add
                    self.score_text.text = str(self.score)

        slider_ends_to_remove = []

        for slider_end in self.slider_ends:
            if slider_end.center_y < (Y_FOR_BUTTON if slider_end.parent_note.type == 'normal' else Y_FOR_GODLY_BUTTON):
                slider_body = next((sb for sb in self.slider_bodies if sb.slider_end == slider_end), None)

                if slider_body:
                    if not slider_body.accuracy_shown:
                        final_accuracy = slider_body.get_final_accuracy()

                        accuracy_text = AccuracyText(final_accuracy, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                        accuracy_text.color = self.accuracy_colors.get(final_accuracy, arcade.color.WHITE)
                        self.accuracy_texts.append(accuracy_text)
                        slider_body.mark_accuracy_shown()

                        if final_accuracy in ["PERFECT", "GREAT", "GOOD"]:
                            self.combo += 1
                            self.stats[final_accuracy.lower()] += 1

                            combo_text = ComboText(self.combo, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
                            self.combo_texts.append(combo_text)
                        elif final_accuracy == "BAD":
                            self.combo = max(0, self.combo - 1)
                            self.stats[final_accuracy.lower()] += 1
                        elif final_accuracy == "MISS":
                            self.combo = 0
                            self.stats[final_accuracy.lower()] += 1

                    if slider_body in self.held_notes:
                        self.held_notes.remove(slider_body)

                slider_ends_to_remove.append((slider_end, slider_body))

        for slider_end, slider_body in slider_ends_to_remove:
            slider_end.remove_from_sprite_lists()
            if slider_body and slider_body in self.slider_bodies:
                self.slider_bodies.remove(slider_body)

        curr_time = time.perf_counter() - self.start_time

        emitters_copy = self.emitters.copy()
        for e in emitters_copy:
            e.update(delta_time)
        for e in emitters_copy:
            if e.can_reap():
                self.emitters.remove(e)

        self.gif_sprites.update_animation()

        self.animation_timer += delta_time

        while self.animation_timer >= self.animation_interval:
            self.update_animations(self.animation_interval)
            self.animation_timer -= self.animation_interval

    def update_animations(self, fixed_delta):
        """Обновление анимаций для оптимизации"""
        texts_to_remove = []
        for i, accuracy_text in enumerate(self.accuracy_texts):
            if not accuracy_text.update(fixed_delta):
                texts_to_remove.append(i)

        for index in reversed(texts_to_remove):
            self.accuracy_texts.pop(index)

        combos_to_remove = []
        for i, combo_text in enumerate(self.combo_texts):
            if not combo_text.update(fixed_delta):
                combos_to_remove.append(i)

        for index in reversed(combos_to_remove):
            self.combo_texts.pop(index)

    def on_key_press(self, key, modifiers):
        for button in self.buttons_list:
            if key == button.key:
                self.check_collisions(button, self.notes_list, False)

        for button in self.godly_buttons_list:
            if key == button.key:
                self.check_collisions(button, self.godly_notes_list, True)

    def on_key_release(self, key, modifiers):
        notes_to_release = []
        for note in self.held_notes:
            if hasattr(note, 'type'):
                if note.type == 'normal':
                    target_button = next((b for b in self.buttons_list if b.row == note.row), None)
                    if target_button and key == target_button.key:
                        notes_to_release.append(note)
                else:
                    target_button = next((b for b in self.godly_buttons_list
                                          if b.row == note.row), None)
                    if target_button and key == target_button.key:
                        notes_to_release.append(note)

        for note in notes_to_release:
            note.release_hold()
            if note in self.held_notes:
                self.held_notes.remove(note)

        sliders_to_release = []
        for slider_body in self.held_notes:
            if hasattr(slider_body, 'note'):
                if slider_body.note.type == 'normal':
                    target_button = next((b for b in self.buttons_list if b.row == slider_body.note.row), None)
                    if target_button and key == target_button.key:
                        sliders_to_release.append(slider_body)
                else:
                    target_button = next((b for b in self.godly_buttons_list
                                          if b.row == slider_body.note.row), None)
                    if target_button and key == target_button.key:
                        sliders_to_release.append(slider_body)

        for slider_body in sliders_to_release:
            accuracy = slider_body.release_hold()

            if accuracy and not slider_body.accuracy_shown:
                accuracy_text = AccuracyText(accuracy, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                accuracy_text.color = self.accuracy_colors.get(accuracy, arcade.color.WHITE)
                self.accuracy_texts.append(accuracy_text)
                slider_body.mark_accuracy_shown()

                if accuracy in ["PERFECT", "GREAT", "GOOD"]:
                    self.combo += 1
                    self.stats[accuracy.lower()] += 1

                    combo_text = ComboText(self.combo, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
                    self.combo_texts.append(combo_text)
                elif accuracy == "BAD":
                    self.combo = max(0, self.combo - 1)
                    self.stats[accuracy.lower()] += 1
                elif accuracy == "MISS":
                    self.combo = 0
                    self.stats[accuracy.lower()] += 1

            if slider_body in self.held_notes:
                self.held_notes.remove(slider_body)

            if slider_body in self.slider_bodies:
                self.slider_bodies.remove(slider_body)

    def check_missed_notes(self):
        """Проверяет ноты, которые пролетели мимо кнопок"""
        notes_to_remove = []
        for note in self.notes_list:
            if note.is_slider and note.is_held:
                continue

            if note.center_y < Y_FOR_BUTTON - 100:
                accuracy_text = AccuracyText("MISS", 500, 400)
                accuracy_text.color = self.accuracy_colors["MISS"]
                self.accuracy_texts.append(accuracy_text)
                notes_to_remove.append(note)

        for note in self.godly_notes_list:
            if note.center_y < Y_FOR_GODLY_BUTTON - 100:
                accuracy_text = AccuracyText("MISS", 500, 400)
                accuracy_text.color = self.accuracy_colors["MISS"]
                self.accuracy_texts.append(accuracy_text)
                notes_to_remove.append(note)

        for note in notes_to_remove:
            if note in self.notes_list:
                note.remove_from_sprite_lists()
                self.combo = 0
                self.stats['miss'] += 1
            elif note in self.godly_notes_list:
                if note.type.lower() == 'demon':
                    new_note = Note('img/Note.png', 0.5, 0,
                                    note.row, 'normal')
                    new_note.center_x = note.center_x
                    new_note.center_y = note.center_y
                    self.notes_list.append(new_note)
                note.remove_from_sprite_lists()
                self.combo = 0

    def check_collisions(self, button, notes_list, is_godly):
        notes_hit_list = arcade.check_for_collision_with_list(button, notes_list)

        if not notes_hit_list:
            return

        closest_note = min(notes_hit_list,
                           key=lambda note: abs(note.center_y - button.center_y))

        distance = abs(closest_note.center_y - button.center_y)
        timing = distance / NOTE_SPEED
        if closest_note.is_slider:

            if distance <= 80:
                closest_note.remove_from_sprite_lists()
                arcade.play_sound(self.hit_sound, volume=master_volume * sfx_volume)

                slider_body = next((sb for sb in self.slider_bodies
                                    if sb.note == closest_note), None)
                if slider_body:
                    slider_body.start_hold()
                    self.held_notes.append(slider_body)

                return

        if timing <= 0.04:
            accuracy = "PERFECT"
            score_mult = PERF_COEFF
            self.combo += 1
        elif timing <= 0.055:
            accuracy = "GREAT"
            score_mult = GREAT_COEFF
            self.combo += 1
        elif timing <= 0.08:
            accuracy = "GOOD"
            score_mult = GOOD_COEFF
            self.combo += 1
        elif timing <= 0.125:
            accuracy = "BAD"
            score_mult = BAD_COEFF
            self.combo = 0
        else:
            accuracy = "MISS"
            score_mult = MISS_COEFF
            self.combo = 0
        self.stats[accuracy.lower()] += 1

        accuracy_text = AccuracyText(accuracy, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        accuracy_text.color = self.accuracy_colors.get(accuracy, arcade.color.WHITE)
        self.accuracy_texts.append(accuracy_text)
        combo_text = ComboText(self.combo, 400, 370)
        self.combo_texts.append(combo_text)
        arcade.play_sound(self.hit_sound, volume=master_volume * sfx_volume)

        particle = Emitter(
            center_xy=(closest_note.center_x, closest_note.center_y),
            emit_controller=EmitBurst(40),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=arcade.make_soft_circle_texture(8, self.accuracy_colors[accuracy]),
                change_xy=arcade.math.rand_on_circle((0.0, 0.0), 5),
                lifetime=random.uniform(0.8, 1.4),
                start_alpha=255, end_alpha=0,
                scale=random.uniform(0.4, 0.7),
                mutation_callback=gravity_drag,
            ),
        )
        self.emitters.append(particle)

        base_score = 100
        if is_godly:
            base_score *= GODLY_COEFF
        self.score += int(base_score * score_mult)
        self.score_text.text = self.score

        if closest_note.type.lower() == 'demon':
            new_note = Note('img/Note.png', 0.5, 0,
                            closest_note.row, 'normal')
            new_note.center_x = closest_note.center_x
            new_note.center_y = closest_note.center_y
            self.notes_list.append(new_note)

        closest_note.remove_from_sprite_lists()


class Note(arcade.Sprite):
    def __init__(self, filename, scale, time, row, type='normal', duration=0):
        global curr_time
        super().__init__(filename, scale)
        self.type = type
        self.speed_y = NOTE_SPEED
        self.time = time
        self.row = row
        self.center_x = 200 * self.row
        self.time_until_hit = self.time - curr_time

        self.duration = duration
        self.is_slider = duration > 0
        self.end_time = self.time + self.duration
        self.is_held = False
        self.hold_start_time = None
        self.progress = 0
        self.slider_end = None

        self.slider_body = None
        if self.duration > 0:
            self.slider_color = arcade.color.YELLOW
            self.slider_width = 30
            self.slider_height = 0

        if self.type == 'normal':
            self.target_y = Y_FOR_BUTTON
        else:
            self.target_y = Y_FOR_GODLY_BUTTON
        self.center_y = self.target_y + self.speed_y * self.time_until_hit

    def update(self, delta_time):
        self.time_until_hit = self.time - curr_time
        self.center_y = self.target_y + self.speed_y * self.time_until_hit

        if self.is_slider and self.slider_end:
            height_diff = self.slider_end.center_y - self.center_y
            self.slider_height = max(0, height_diff)

            if self.is_held:
                self.slider_color = arcade.color.GREEN
            else:
                self.slider_color = arcade.color.YELLOW

    def start_hold(self):
        self.is_held = True
        self.hold_start_time = curr_time
        self.color = arcade.color.GREEN

    def release_hold(self):
        self.is_held = False
        self.color = arcade.color.WHITE


class SliderBody(arcade.Sprite):
    def __init__(self, note, slider_end):
        super().__init__()
        self.note = note
        self.slider_end = slider_end
        self.color = arcade.color.YELLOW
        self.width = 30
        self.is_held = False
        self.hold_start_time = None
        self.duration = note.duration
        self.last_score_time = curr_time
        self.score_interval = 0.1
        self.hold_score = 0
        self.max_score = 50 * self.duration
        self.score_per_interval = 5
        self.accuracy_shown = False
        self.hold_progress = 0.0

    def update(self):
        if self.note and self.slider_end:
            self.center_x = self.note.center_x
            self.center_y = (self.note.center_y + self.slider_end.center_y) / 2
            self.height = abs(self.slider_end.center_y - self.note.center_y)

            if self.is_held:
                self.color = arcade.color.GREEN
                if self.hold_start_time is not None:
                    hold_duration = curr_time - self.hold_start_time
                    self.hold_progress = min(1.0, hold_duration / self.duration)
            else:
                self.color = arcade.color.WHITE

    def draw(self):
        """Отрисовка тела слайдера"""
        if self.height > 0:
            arcade.draw_lrbt_rectangle_filled(
                self.center_x - self.width / 2,
                self.center_x + self.width / 2,
                min(self.note.center_y, self.slider_end.center_y),
                max(self.note.center_y, self.slider_end.center_y),
                self.color
            )

    def start_hold(self):
        self.is_held = True
        self.hold_start_time = curr_time
        self.last_score_time = curr_time
        self.hold_score = 0
        self.accuracy_shown = False
        self.hold_progress = 0.0

    def release_hold(self):
        self.is_held = False
        if not self.accuracy_shown:
            accuracy = self.get_accuracy_for_release()
            return accuracy
        return None

    def update_hold_score(self):
        """Обновляет очки за удержание"""
        if not self.is_held or self.hold_start_time is None:
            return 0

        if curr_time - self.last_score_time < self.score_interval:
            return 0

        hold_duration = curr_time - self.hold_start_time
        self.hold_progress = min(1.0, hold_duration / self.duration)

        if self.hold_progress < 1.0:
            score_to_add = self.score_per_interval
            self.hold_score += score_to_add
            self.last_score_time = curr_time
            return score_to_add

        return 0

    def get_accuracy_for_release(self):
        """Определяет точность при отпускании слайдера"""
        if self.hold_progress >= 0.9:
            return "PERFECT"
        elif self.hold_progress >= 0.7:
            return "GREAT"
        elif self.hold_progress >= 0.5:
            return "GOOD"
        elif self.hold_progress > 0:
            return "BAD"
        else:
            return "MISS"

    def get_final_accuracy(self):
        """Определяет точность удержания слайдера при достижении конца"""
        if self.hold_progress >= 0.9:
            return "PERFECT"
        elif self.hold_progress >= 0.7:
            return "GREAT"
        elif self.hold_progress >= 0.5:
            return "GOOD"
        elif self.hold_progress > 0:
            return "BAD"
        else:
            return "MISS"

    def get_total_hold_score(self):
        return int(self.hold_score)

    def mark_accuracy_shown(self):
        self.accuracy_shown = True


class SliderEnd(arcade.Sprite):
    def __init__(self, filename, scale, time, row, parent_note):
        super().__init__(filename, scale)
        self.time = time
        self.row = row
        self.parent_note = parent_note
        self.center_x = 200 * self.row

        if parent_note.type == 'normal':
            self.target_y = Y_FOR_BUTTON
        else:
            self.target_y = Y_FOR_GODLY_BUTTON

        self.time_until_hit = self.time - curr_time
        self.speed_y = NOTE_SPEED
        self.center_y = self.target_y + self.speed_y * self.time_until_hit

    def update(self, delta_time):
        self.time_until_hit = self.time - curr_time
        self.center_y = self.target_y + self.speed_y * self.time_until_hit


class Button(arcade.Sprite):
    def __init__(self, filename, scale, key, row, type='normal'):
        super().__init__(filename, scale)
        self.type = type
        self.is_clicked = False
        self.key = key
        self.center_x = 200 * row
        self.row = row
        if type == 'normal':
            self.center_y = Y_FOR_BUTTON
        else:
            self.center_y = Y_FOR_GODLY_BUTTON


# --- Секция PyQt6 ---
class StartMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(SCREEN_TITLE)
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

    def show_after_game(self):
        """Показываем окно после закрытия игры"""
        self.show()
        self.raise_()
        self.activateWindow()


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
        self.btn_song_butcher_vanity.clicked.connect(lambda: self.start_game('butcher_vanity'))

    def start_game(self, song):
        global curr_song
        curr_song = song

        # self.window().hide()
        self.window().close()

        launch_arcade_game()


def launch_arcade_game():
    global START_GAME

    if not START_GAME:
        START_GAME = True

        window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1 / int(fps))
        game_view = GameView()
        window.show_view(game_view)


        arcade.run()
        arcade.stop_sound(game_view.player)

        # Крашит, мб для себя пофикшу
        '''START_GAME = False

        windows = app.topLevelWidgets()
        if windows:
            main_window = windows[0]
            main_window.close()
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()'''


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/Settings.ui', self)
        self.setWindowTitle('Settings')
        self.setFixedSize(800, 700)

        saved_settings = cfg_mng.load_settings_to_vars()

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
        self.tempFPS = int(self.lineEdit_FPS.text())

    def save_changes(self):
        global master_volume, music_volume, sfx_volume, fps
        self.FPS = self.tempFPS
        self.master_volume = self.tempmastervolume
        self.music_volume = self.tempmusicvolume
        self.sfx_volume = self.tempsfxvolume
        master_volume = self.master_volume / 100
        music_volume = self.music_volume / 100
        sfx_volume = self.sfx_volume / 100
        if fps <= 0 or not fps.isdigit():
            fps = 60
        else:
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
    global app
    app = QApplication(sys.argv)
    menu = StartMenu()
    menu.show()
    app.exec()


if __name__ == '__main__':
    main()

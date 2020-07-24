import re
import os
os.environ['KIVY_AUDIO'] = 'sdl2'
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from src.frontend.custom_widgets.PlaygroundWidget import Playground
from src.frontend.custom_widgets.RuleWidget import *
from src.frontend.custom_widgets.WinningWidget import WinningWidget

Builder.load_file(KV_FILE_PATH)


class MenuScreen(Screen):
    pass


class LevelsScreen(Screen):

    def on_enter(self, *args):
        btn_list = self.children[0].children[0].children
        for obj in btn_list:
            if type(obj) is Button:
                lvl = int(re.search(r'\d+', obj.text).group())
                obj.background_color = self.get_button_color(lvl)

    @staticmethod
    def get_button_color(lvl):
        if storage.get('lvl' + str(lvl))['status'] == 'Passed':
            return 1, 1, 0, 1
        elif storage.get('lvl' + str(lvl))['status'] == 'Unlocked':
            return 1, 0, 1, 1
        return 1, 1, 1, 1

    @staticmethod
    def go_to_lvl(lvl):
        if storage.get('lvl' + str(lvl))['status'] == 'Locked':
            # Level is locked
            return
        sm.get_screen('game').lvl = lvl
        sm.current = 'game'


class GameScreen(Screen):
    playground = ObjectProperty(None, allownone=True)
    lvl = NumericProperty()
    winning_widget = ObjectProperty(None, allownone=True)

    def on_enter(self, *args):
        self.playground = Playground(storage=storage)
        self.playground.start(self.lvl)
        self.add_widget(self.playground)
        self.set_buttons()

    def restart(self):
        self.clean()
        self.set_buttons()
        self.on_enter()

    def clean(self):
        if self.playground is not None:
            self.playground.update_event.cancel()
            self.remove_widget(self.playground)
            self.playground = None
        if self.winning_widget is not None:
            self.remove_widget(self.winning_widget)
            self.winning_widget = None

    def switch_field(self):
        self.playground.switch_field()

    def show_all_rules(self):
        self.playground.show_all_rules()

    def set_buttons(self):
        self.ids.field_switch.text = 'to target\nfield'

    def show_winning_widget(self):
        self.winning_widget = WinningWidget()
        self.add_widget(self.winning_widget)
        sound = SoundLoader.load(join(SOUND_PATH, 'moan.ogg'))
        if sound:
            print("Sound found at %s" % sound.source)
            print("Sound is %.3f seconds" % sound.length)
            sound.play()
        else:
            print('fail')

    def go_to_next_lvl(self):
        self.clean()
        self.lvl += 1
        self.on_enter()


storage = JsonStore(STORAGE_PATH)


# Call only once at first start
def init_storage():
    storage.put('lvl0', status='Unlocked')
    for i in range(1, 15):
        storage.put('lvl' + str(i), status='Locked')


init_storage()

sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(LevelsScreen(name='levels'))
sm.add_widget(GameScreen(name='game'))
sm.current = 'levels'


class Crystal_game(App):

    def build(self):
        return sm


if __name__ == '__main__':
    Crystal_game().run()

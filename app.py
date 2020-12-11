import os
import requests

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivysrc.main_screen import MainScreen
from kivysrc.file_browser import AlertDialog
from settings import MAIN_SCREEN, APP_HEIGHT, APP_WIDTH, CHECK_URL

Config.read(os.path.expanduser('~/.kivy/config.ini'))
Config.set('graphics', 'resizeable', '0')
Config.set('graphics', 'width', str(APP_WIDTH))
Config.set('graphics', 'height', str(APP_HEIGHT))
Config.set('kivy', 'keyboard_mode', 'system')
Config.set('graphics', 'keyboard_mode', 'en_US')
Config.set('graphics', 'log_level', 'info')

Config.write()
Window.size = (int(APP_WIDTH), int(APP_HEIGHT))


class ImageConverterTool(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_screen = MainScreen(name=MAIN_SCREEN)

        screens = [
            self.main_screen
        ]

        self.sm = ScreenManager()
        for screen in screens:
            self.sm.add_widget(screen)

    @staticmethod
    def check_url():
        res = requests.get(CHECK_URL)
        if res.status_code == 200:
            return True
        else:
            return False

    def build(self):
        if self.check_url():
            self.sm.current = MAIN_SCREEN
            return self.sm
        else:
            warning_popup = AlertDialog(f"File Corrupted!")
            warning_popup.open()

    def on_stop(self):
        Window.close()


if __name__ == '__main__':

    ImageConverterTool().run()

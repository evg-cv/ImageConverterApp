import threading
import datetime
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from src.db.manager import DatabaseManager
from settings import MAIN_SCREEN_PATH


Builder.load_file(MAIN_SCREEN_PATH)


class MainScreen(Screen):
    capture = None
    event_take_video = None
    texture = None

    def __init__(self, **kwargs):

        super(MainScreen, self).__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.display_ret = False
        self.display_thread = None
        self.pause_ret = False
        self.ids.video.egg_counter.radius_min = int(self.ids.radius_min.text)
        self.ids.video.egg_counter.radius_max = int(self.ids.radius_max.text)
        self.ids.video.egg_counter.area_min = int(self.ids.area_min.text)
        self.ids.video.egg_counter.area_max = int(self.ids.area_max.text)

    def on_enter(self, *args):
        self.ids.video.start()

    def on_leave(self, *args):
        self.ids.video.stop()
        super(MainScreen, self).on_leave(*args)

    def start_counting(self, stop_ret=True):
        if stop_ret:
            self.ids.video.egg_counter.egg_num = 0
            self.ids.pause_btn.text = "Pause"
        self.ids.video._egg_counter_ret = True
        self.display_ret = True
        self.display_thread = threading.Thread(target=self.display_egg_number)
        self.display_thread.start()

    def stop_counting(self, stop_ret=True):
        self.ids.video._egg_counter_ret = False
        self.display_ret = False
        if self.display_thread is not None:
            self.display_thread.join()
        if stop_ret:
            self.ids.egg_num.text = "0"
            self.pause_ret = False
            self.ids.pause_btn.text = "Pause"
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db_manager.insert_data(egg_num=str(self.ids.video.egg_counter.egg_num), t_stamp=current_time)

    def pause_counting(self):
        if (self.display_ret and not self.pause_ret) or (not self.display_ret and self.pause_ret):
            self.pause_ret = not self.pause_ret
            if self.pause_ret:
                self.ids.pause_btn.text = "Resume"
                self.stop_counting(stop_ret=False)
            else:
                self.ids.pause_btn.text = "Pause"
                self.start_counting(stop_ret=False)

    def display_previous_number(self):
        if not self.display_ret:
            self.ids.egg_num.text = self.db_manager.read_previous_data()

    def display_egg_number(self):
        while True:
            if not self.display_ret:
                break
            self.ids.egg_num.text = str(self.ids.video.egg_counter.egg_num)
            time.sleep(0.1)

    def set_radius_min(self):
        self.ids.video.egg_counter.radius_min = int(self.ids.radius_min_slider.value)

    def set_radius_max(self):
        self.ids.video.egg_counter.radius_max = int(self.ids.radius_max_slider.value)

    def set_area_min(self):
        self.ids.video.egg_counter.area_min = int(self.ids.area_min_slider.value)

    def set_area_max(self):
        self.ids.video.egg_counter.area_max = int(self.ids.area_max_slider.value)

    def close_window(self):
        self.display_ret = False
        self.display_thread.join()
        App.get_running_app().stop()

    def on_close(self):
        pass

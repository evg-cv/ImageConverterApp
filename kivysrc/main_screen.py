import os
import cv2
import ntpath
from PIL import Image

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from functools import partial
from kivysrc.file_browser import LoadDialog, AlertDialog
from utils.image_tool import get_round_chamfer_image, add_spot_channel
from settings import MAIN_SCREEN_PATH, DPI, INCH


Builder.load_file(MAIN_SCREEN_PATH)


class MainScreen(Screen):
    round = ObjectProperty(None)
    chamfer = ObjectProperty(None)
    zoom_in = ObjectProperty(None)
    zoom_out = ObjectProperty(None)
    rot_90 = ObjectProperty(None)
    rot_180 = ObjectProperty(None)
    rot_270 = ObjectProperty(None)
    filePath = StringProperty('')

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Window.bind(on_dropfile=self._on_file_drop)
        self.file_path = None
        self.file_name = None

    @staticmethod
    def convert_dist_to_pixel(dist):
        return int(dist * DPI / INCH)

    def _on_file_drop(self, window, file_path):
        print(file_path)
        full_path = file_path.decode("utf-8")  # convert byte to string
        self.ids.image.source = full_path
        self.file_name = ntpath.basename(file_path).decode("utf-8")
        self.file_path = full_path.replace(self.file_name, "")
        self.file_name = self.file_name.replace(".png", "")
        self.ids.image.reload()

    def open_image(self):
        file_browser = LoadDialog()
        file_browser.bind(on_confirm=partial(self.get_selected_file))
        file_browser.open()

    def get_selected_file(self, *args):
        args[0].dismiss()
        self.file_path = args[1]
        file_name = args[2][0]
        self.file_name = file_name.replace(".png", "")
        file_full_path = os.path.join(self.file_path, file_name)
        self.ids.image.source = file_full_path

    def process_image(self):
        output_tiff_path = os.path.join(self.file_path, f"{self.file_name}.tiff")
        output_png_path = os.path.join(self.file_path, f"{self.file_name}.png")
        frame = cv2.imread(os.path.join(self.file_path, f"{self.file_name}.png"))
        if self.rot_90.active:
            rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.rot_180.active:
            rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
        else:
            rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        if self.round.active:
            round_chamfer_ret = "round"
        else:
            round_chamfer_ret = "chamfer"
        if self.zoom_in.active:
            zoom_ret = "in"
        else:
            zoom_ret = "out"

        r_img_width = self.convert_dist_to_pixel(dist=int(self.ids.img_width.text))
        r_img_height = self.convert_dist_to_pixel(dist=int(self.ids.img_height.text))
        round_chamfer_value = self.convert_dist_to_pixel(dist=float(self.ids.round_value.text))
        spot_number = int(self.ids.spot_number.text)
        zoom_value = self.convert_dist_to_pixel(dist=float(self.ids.zoom_value.text))
        resized_frame = cv2.resize(rotated_frame, (r_img_width, r_img_height), interpolation=cv2.INTER_AREA)
        round_chamfer_image = get_round_chamfer_image(frame=resized_frame, radius=round_chamfer_value,
                                                      round_chamfer=round_chamfer_ret)
        spot_image = add_spot_channel(frame=resized_frame, radius=round_chamfer_value, ch_num=spot_number,
                                      zoom_value=zoom_value, zoom_ret=zoom_ret, round_chamfer=round_chamfer_ret,
                                      round_chamfer_image=round_chamfer_image)
        cv2.imwrite(output_png_path, spot_image)
        png_image = Image.open(output_png_path)
        cmyk_image = png_image.convert('CMYK')
        cmyk_image.save(output_tiff_path)
        warning_popup = AlertDialog(f"Saved in {output_tiff_path}!")
        warning_popup.open()

    def on_enter(self, *args):
        pass

    def on_leave(self, *args):
        super(MainScreen, self).on_leave(*args)

    def on_close(self):
        pass

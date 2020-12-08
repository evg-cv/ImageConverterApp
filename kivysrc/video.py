# import time
import cv2
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from utils.frame_buf import frame_to_buf
from kivy.uix.image import Image
from kivy.logger import Logger
from src.egg.counter import EggCounter
from settings import BAD_FRAME_PATH, VIDEO_PATH


class VideoWidget(Image):
    """:class:`KioskVideoWidget` is an implementation of the video live feed.

    Call `start()` function to start live video feed on this widget,
    and call `pause()` function to pause.

    Attention: Make sure to call `stop()` function before moving to other screen!!!
               e.g. If this widget is used in a `Screen` widget, make use to
               add `stop()` function in its `on_leave()` function!
    """

    _event_take_video = None

    _capture = None

    port_num = ObjectProperty(-1, allownone=True)
    thresh_value = ObjectProperty(-1, allownone=True)
    """Port number of video source.
    When using camera directly, this should be a numeric value.
    When getting video feed from REDIS, a string value should be used.
    :attr:`port_num` is an :class:`~kivy.properties.ObjectProperty` and defaults to -1.
    """

    camera_width = NumericProperty(640)
    """Pixel width of camera.
    :attr:`camera_width` is an :class:`~kivy.properties.NumericProperty` and defaults to 1280. (720p)
    """

    camera_height = NumericProperty(480)
    """Pixel height of camera.
    :attr:`camera_height` is an :class:`~kivy.properties.NumericProperty` and defaults to 720. (720p)
    """

    is_running = BooleanProperty(False)

    _frame = None

    def __init__(self, **kwargs):
        self._egg_counter_ret = None
        self.egg_counter = EggCounter()
        super(VideoWidget, self).__init__(**kwargs)

    def on_port_num(self, *args):
        """
        This function should be called once this widget is created.
        If we call this function in self.__init__() function, height & width will have default value.
        :param args:
        :return:
        """
        try:
            if VIDEO_PATH == "":
                self._capture = cv2.VideoCapture(self.port_num)
            else:
                self._capture = cv2.VideoCapture(VIDEO_PATH)
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            self._frame = None
        except Exception as e:
            Logger.error('KioskVideoWidget: Failed to assign port number - {}'.format(e))
            self._capture = None

    def start(self):
        """
        Start live video feed
        :return:
        """
        if self.is_running:
            return

        if self.port_num is not None:
            if self._capture is None:
                self.on_port_num()

            if self._event_take_video is None:
                self._event_take_video = Clock.schedule_interval(lambda dt: self._take_video(), 1.0 / 30.0)
            else:
                self._event_take_video()
            self.is_running = True
        else:
            self.source = BAD_FRAME_PATH
            Logger.warning('KioskVideo: Port is not set yet')

    def pause(self):
        if self._event_take_video and self._event_take_video.is_triggered:
            self._event_take_video.cancel()
            self._event_take_video = None
        self.is_running = False

    def _take_video(self):
        """
        Capture video frame and update image widget
        :return:
        """
        try:
            if type(self.port_num) == int:
                ret, frame = self._capture.read()
            else:
                frame = None
            if self._egg_counter_ret:
                counted_frame = self.egg_counter.count(frame=frame)
            else:
                counted_frame = frame
        except (cv2.error, AttributeError, ConnectionError):
            counted_frame = None
        self._update_video(origin_frame=counted_frame)

    def _update_video(self, origin_frame, *args):
        """
        Display captured image to the widget
        :return:
        """
        texture = frame_to_buf(frame=origin_frame)
        if texture is None:
            self.source = BAD_FRAME_PATH
        else:
            self.texture = texture
            self._frame = origin_frame

    def get_frame(self):
        return self._frame

    def save_to_file(self, filename):
        if self._frame is not None:
            try:
                cv2.imwrite(filename, self._frame)
                return filename
            except Exception as e:
                Logger.error('KioskVideoWidget: Failed to save to file, reason - {}'.format(e))
        else:
            Logger.error('KioskVideoWidget: Tried to save to file, but current frame is none!')

    def stop(self):
        self.pause()
        try:
            if self._capture is not None:
                self._capture.release()
                self._capture = None
        except AttributeError:
            pass

from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from settings import BROWSER_SCREEN_PATH

Builder.load_file(BROWSER_SCREEN_PATH)


class LoadDialog(Popup):
    error = StringProperty()

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self.register_event_type('on_confirm')

    def on_error(self, inst, text):
        if text:
            self.lb_error.height = 30
            self.height += 30
        else:
            self.lb_error.size_hint_y = None
            self.lb_error.height = 0
            self.size -= 30

    def dismiss_popup(self):
        self.dismiss()

    def load(self):

        if not self.path or not self.filename:
            self.error = "Error: select file"
        else:
            file_ext = self.filename[0][self.filename[0].rfind(".") + 1:]
            if "png" not in file_ext.lower():
                self.error = "Select the PNG file"
            else:
                self.dispatch('on_confirm', self.path, self.filename)

    def on_confirm(self, *args):
        pass


class AlertDialog(Popup):

    label = StringProperty()

    def __init__(self, label, **kwargs):
        super(AlertDialog, self).__init__(**kwargs)
        self.set_description(label)

    def set_description(self, label):
        self.label = label


if __name__ == '__main__':
    LoadDialog()

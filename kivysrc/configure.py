import os
from kivy.clock import Clock
from kivy.config import Config

Config.read(os.path.expanduser('~/.kivy/config.ini'))
Config.set('graphics', 'width', str(600))
Config.set('graphics', 'height', str(480))
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('input', 'mtdev_%(name)s', 'probesysfs,provider=mtdev')
Config.set('input', 'hid_%(name)s', 'probesysfs,provider=hidinput')
Config.remove_option('input', '%(name)s')

Clock.max_iteration = 20

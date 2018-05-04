# pylint: disable=E0611
# -*- coding: utf-8 -*-
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import ObjectProperty
from kivy.vector import Vector
from kivy.config import Config
from random import randint

class MonitorDeviceWidget(Widget):
    pass

class MonitorApp(App):
    def build(self):
        return MonitorDeviceWidget()

if __name__ == '__main__':
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '480')
    MonitorApp().run()

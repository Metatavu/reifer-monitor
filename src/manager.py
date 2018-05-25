# Copyright (C) 2018 Metatavu Oy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# pylint: disable=E0611
# -*- coding: utf-8 -*-

import os
import sys
from typing import Any, Callable, Dict, List, NamedTuple, Optional

import toml
from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.properties import (ListProperty, NumericProperty, ObjectProperty,
                             StringProperty, BooleanProperty)
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput

from client_model import Device, Sensor, WorkstationState
from fakesensors import BlinkingSensorSystem
from serverconnection import ServerConnection
import os


class ValidatingTextInput(TextInput):
    valid: BooleanProperty = BooleanProperty()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.bind(text=self.on_text)

    def on_text(self, instance: Widget, value: str) -> None:
        if len(value) == 10:
            self.valid = True
        else:
            self.valid = False
        if self.valid:
            self.background_color = [0.5, 1, 0.5, 1]
        else:
            self.background_color = [1, 0.5, 0.5, 1]


class CardManagerWidget(Widget):
    _server_connection: ServerConnection
    batch_name: StringProperty = StringProperty('')
    batch_code: StringProperty = StringProperty('')

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super().__init__()
        self._server_connection = ServerConnection(sys.argv[1])
        self._server_connection.connect()

    def on_associate(self) -> None:
        print(f"batch_name: {self.batch_name}, batch_code: {self.batch_code}")
        self._server_connection.associate_batch(self.batch_code, self.batch_name)


class ManagerApp(App):
    def build(self) -> Any:
        self.widget = CardManagerWidget()
        return self.widget


if __name__ == '__main__':
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '300')
    ManagerApp().run()

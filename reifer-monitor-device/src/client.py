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
from typing import NamedTuple
from typing import List
from typing import Optional
from typing import Callable
from typing import Dict
from typing import Any
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.config import Config
from kivy.graphics import Color
from fakesensors import BlinkingSensorSystem
from client_model import Device
from client_model import Sensor
from client_model import WorkstationState
from serverconnection import ServerConnection


class SensorStatus(NamedTuple):
    name: str
    status: str
    color: Color


class MonitorDeviceWidget(Widget):
    num_workers: NumericProperty = NumericProperty()
    batch_name: StringProperty = StringProperty('')
    batch_code: StringProperty = StringProperty('')
    workstation_color_r: NumericProperty = NumericProperty()
    workstation_color_g: NumericProperty = NumericProperty()
    workstation_color_b: NumericProperty = NumericProperty()
    workstation_color_a: NumericProperty = NumericProperty()
    workstation_state: StringProperty = StringProperty('')
    sensor_statuses: ListProperty = ListProperty([
        SensorStatus("", "", Color(0,0,0,0)),
        SensorStatus("", "", Color(0,0,0,0)),
        SensorStatus("", "", Color(0,0,0,0)),
        SensorStatus("", "", Color(0,0,0,0)),
        SensorStatus("", "", Color(0,0,0,0))
    ])

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super().__init__()
        self.blinker = BlinkingSensorSystem([
            Sensor(1, "Sensor 1", True),
            Sensor(2, "Sensor 2", False),
            Sensor(3, "Sensor 3", False),
            Sensor(4, "Sensor 4", True)])
        server_connection = ServerConnection("tcp://localhost:5555")
        server_connection.connect()
        model = Device("WS", self.blinker, server_connection)
        self.num_workers = model.num_workers
        self.on_sensors_model_change(model.sensors)
        model.add_num_workers_changed_listener(self.on_num_workers_model_change)
        model.add_sensors_changed_listener(self.on_sensors_model_change)
        model.add_workstation_state_changed_listener(self.on_workstation_state_model_change)
        model.add_batch_name_changed_listener(self.on_batch_name_model_change)
        self.model = model
        self.bind(num_workers=self.on_num_workers_change)

    def stop(self) -> None:
        self.blinker.stop()

    def on_num_workers_change(self, instance: Widget, value: int) -> None:
        self.model.num_workers = value

    def on_batch_code_input(self, value: str) -> None:
        self.model.batch_code = value
        self.batch_code = value

    def on_num_workers_model_change(self, num_workers: int) -> None:
        self.num_workers = num_workers

    def on_sensors_model_change(self, sensors: List[Sensor]) -> None:
        aux: List[Optional[Sensor]] = [None] * 5
        aux[:len(sensors)] = sensors
        self.sensor_statuses = [self._compute_sensor_status(x) for x in aux]

    def on_batch_name_model_change(self, batch_name: str) -> None:
        self.batch_name = batch_name

    def on_workstation_state_model_change(self, state: WorkstationState) -> None:
        if state == WorkstationState.EMPTY:
            self.workstation_color_r = 0.67
            self.workstation_color_g = 0.125
            self.workstation_color_b = 0
            self.workstation_color_a = 1
            self.workstation_state = "TYHJÄ"
        elif state == WorkstationState.IDLE:
            self.workstation_color_r = 0.5
            self.workstation_color_g = 0.5
            self.workstation_color_b = 0
            self.workstation_color_a = 1
            self.workstation_state = "EI KÄYTÖSSÄ"
        elif state == WorkstationState.ACTIVE:
            self.workstation_color_r = 0
            self.workstation_color_g = 0.67
            self.workstation_color_b = 0.375
            self.workstation_color_a = 1
            self.workstation_state = "KÄYTÖSSÄ"

    def _compute_sensor_status(self, sensor: Optional[Sensor]) -> SensorStatus:
        if sensor is None:
            return SensorStatus("", "", Color(0, 0, 0, 0))
        if sensor.active:
            status = "AKTIIVINEN"
            color = Color(0, 0.67, 0.375, 1)
        else:
            status = "EI AKTIIVINEN"
            color = Color(0.67, 0.125, 0, 1)
        return SensorStatus(sensor.name, status, color)


class MonitorApp(App):
    def build(self) -> Any:
        self.widget = MonitorDeviceWidget()
        return self.widget

    def on_stop(self) -> None:
        self.widget.stop()


if __name__ == '__main__':
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '480')
    MonitorApp().run()

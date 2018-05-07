# pylint: disable=E0611
# -*- coding: utf-8 -*-
from typing import NamedTuple
from typing import List
from typing import Optional
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.config import Config
from kivy.graphics import Color
from reifermonitor.fakesensors import BlinkingSensorSystem
from reifermonitor.model import Device
from reifermonitor.model import Sensor
from reifermonitor.model import WorkstationState


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

    def __init__(self, **kwargs) -> None:
        super().__init__()
        model = Device(
            BlinkingSensorSystem(
                [Sensor(1, "Sensor 1", True),
                 Sensor(2, "Sensor 2", False),
                 Sensor(3, "Sensor 3", False),
                 Sensor(4, "Sensor 4", True)]))
        self.num_workers = model.num_workers
        self.on_sensors_model_change(model.sensors)
        model.add_num_workers_changed_listener(self.on_num_workers_model_change)
        model.add_sensors_changed_listener(self.on_sensors_model_change)
        model.add_workstation_state_changed_listener(self.on_workstation_state_model_change)
        self.model = model
        self.bind(num_workers=self.on_num_workers_change)

    def on_num_workers_change(self, instance: Widget, value: int) -> None:
        self.model.num_workers = value

    def on_batch_code_input(self, value: str) -> None:
        self.batch_code = value

    def on_num_workers_model_change(self, num_workers: int) -> None:
        self.num_workers = num_workers

    def on_sensors_model_change(self, sensors: List[Sensor]) -> None:
        aux: List[Optional[Sensor]] = [None] * 5
        aux[:len(sensors)] = sensors
        self.sensor_statuses = [self._compute_sensor_status(x) for x in aux]

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
    def build(self):
        return MonitorDeviceWidget()


if __name__ == '__main__':
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '480')
    MonitorApp().run()
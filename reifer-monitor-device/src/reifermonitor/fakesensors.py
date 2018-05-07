from typing import List
from typing import Callable
from reifermonitor.model import Sensor
from reifermonitor.model import SensorSystem
import random
import threading
import time


class BlinkingSensorSystem(SensorSystem):
    _sensors: List[Sensor]
    _sensor_change_listeners: List[Callable[[Sensor], None]]

    def __init__(self, sensors: List[Sensor]) -> None:
        self._sensors = sensors
        self._sensor_change_listeners = []
        def blinker():
            while True:
                time.sleep(1)
                i = random.randrange(0, len(self._sensors))
                old_sensor = self._sensors[i]
                new_sensor = old_sensor._replace(active=not old_sensor.active)
                self._sensors[i] = new_sensor
                for listener in self._sensor_change_listeners:
                    listener(new_sensor)
        threading.Thread(target=blinker).start()

    @property
    def sensors(self) -> List[Sensor]:
        return self._sensors

    def add_sensor_change_listener(
            self,
            listener: Callable[[Sensor], None]) -> None:
        self._sensor_change_listeners.append(listener)

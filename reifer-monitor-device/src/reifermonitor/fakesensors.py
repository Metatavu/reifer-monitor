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
        self.running = True
        self._sensors = sensors
        self._sensor_change_listeners = []
        def blinker():
            while self.running:
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

    def stop(self) -> None:
        self.running = False

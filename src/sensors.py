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

from typing import TYPE_CHECKING, Callable, Dict, List, Tuple, Any
from operator import itemgetter
from enum import Enum
from sys import stderr

from client_model import SensorSystem as SensorSystemInterface
from client_model import Sensor

if TYPE_CHECKING:
    import fakewiringpi as wiringpi
else:
    try:
        import wiringpi
    except ImportError:
        import fakewiringpi as wiringpi


class QuickAmplitudeMeasurer:
    _bias: int
    _threshold: int
    _averaging: int
    _values: List[float]

    def __init__(self, bias: int, threshold: int, averaging: int) -> None:
        self._bias = bias
        self._threshold = threshold
        self._averaging = averaging
        self._values = []

    def sample(self, value: int) -> None:
        unbiased = value - self._bias
        self._values.append(abs(unbiased))
        while len(self._values) > self._averaging:
            self._values.pop(0)

    def over_threshold(self) -> bool:
        if len(self._values) < self._averaging:
            return False
        else:
            return (sum(self._values) / len(self._values)) > self._threshold


class SensorSystem(SensorSystemInterface):
    _vibration_active: bool
    _vibration_sample: bool
    _time_since_vibration_change: int
    _current_off_time: int
    _current_active: bool
    _current_measurer: QuickAmplitudeMeasurer
    _sensor_change_listeners: List[Callable[[Sensor], None]]
    _schedule: Tuple[Callable[[Callable[..., None]], None]]

    def __init__(self,
            schedule: Callable[[Callable[..., None]], None]) -> None:
        self._vibration_active = False
        self._vibration_sample = False
        self._time_since_vibration_change = 10000
        self._current_off_time = 10000
        self._current_active = False
        self._sensor_change_listeners = []
        self._schedule = (schedule,)
        self._current_measurer = self._new_measurer()

    def _new_measurer(self) -> QuickAmplitudeMeasurer:
        return QuickAmplitudeMeasurer(2048, 11, 256)

    def start(self) -> None:
        schedule, = self._schedule
        schedule(self.update)

    def update(self, *args: Any) -> None:
        vibration_sample = bool(wiringpi.digitalRead(0))
        if self._vibration_sample != vibration_sample:
            self._vibration_sample = vibration_sample
            self._time_since_vibration_change = 0
        self._time_since_vibration_change += 1
        vibration_active = self._time_since_vibration_change < 300
        if self._vibration_active != vibration_active:
            self._vibration_active = vibration_active
            for listener in self._sensor_change_listeners:
                listener(Sensor(1, "Tärinä", vibration_active))
        current_sample = wiringpi.analogRead(0)
        self._current_measurer.sample(current_sample)
        if self._current_measurer.over_threshold():
            self._current_off_time = 0
        else:
            self._current_off_time += 1
        current_active = self._current_off_time < 500
        if self._current_active != current_active:
            self._current_active = current_active
            for listener in self._sensor_change_listeners:
                listener(Sensor(2, "Virta", current_active))
        schedule, = self._schedule
        schedule(self.update)

    @property
    def sensors(self) -> List[Sensor]:
        return [
            Sensor(1, "Tärinä", self._vibration_active),
            Sensor(2, "Virta", self._current_active)
        ]

    def add_sensor_change_listener(
            self,
            listener: Callable[[Sensor], None]) -> None:
        self._sensor_change_listeners.append(listener)

# vim: tw=80 sw=4 ts=4 expandtab:
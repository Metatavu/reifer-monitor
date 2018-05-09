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

from typing import Callable
from typing import List
from typing import NamedTuple
from abc import ABCMeta
from abc import abstractmethod
from enum import Enum


class Sensor(NamedTuple):
    identifier: int
    name: str
    active: bool


class SensorSystem(metaclass=ABCMeta):
    @property
    @abstractmethod
    def sensors(self) -> List[Sensor]:
        pass

    @abstractmethod
    def add_sensor_change_listener(
            self,
            listener: Callable[[Sensor], None]) -> None:
        pass


class WorkstationState(Enum):
    EMPTY = 1
    IDLE = 2
    ACTIVE = 3


class Device:
    _sensor_system: SensorSystem
    _num_workers: int
    _workstation_state_changed_listeners: List[Callable[[WorkstationState], None]]
    _num_workers_changed_listeners: List[Callable[[int], None]]
    _sensors_changed_listeners: List[Callable[[List[Sensor]], None]]

    def __init__(
            self,
            sensor_system: SensorSystem) -> None:
        self._sensor_system = sensor_system
        self._num_workers = 0
        self._workstation_state_changed_listeners = []
        self._num_workers_changed_listeners = []
        self._sensors_changed_listeners = []
        sensor_system.add_sensor_change_listener(self._on_sensor_changed)

    def add_workstation_state_changed_listener(
            self,
            listener: Callable[[WorkstationState], None]) -> None:
        self._workstation_state_changed_listeners.append(listener)

    def add_num_workers_changed_listener(
            self,
            listener: Callable[[int], None]) -> None:
        self._num_workers_changed_listeners.append(listener)

    def add_sensors_changed_listener(
            self,
            listener: Callable[[List[Sensor]], None]) -> None:
        self._sensors_changed_listeners.append(listener)

    def _on_sensor_changed(self, new_sensor: Sensor) -> None:
        sensors = self._sensor_system.sensors
        for sensor_listener in self._sensors_changed_listeners:
            sensor_listener(sensors)
        workstation_state = self.workstation_state
        for workstation_listener in self._workstation_state_changed_listeners:
            workstation_listener(workstation_state)

    @property
    def num_workers(self) -> int:
        return self._num_workers

    @num_workers.setter
    def num_workers(self, num_workers: int) -> None:
        if num_workers < 0:
            raise ValueError(f"num_workers must be >=0, was {num_workers}")

        if num_workers > 4:
            raise ValueError(f"num_workers must be <=4, was {num_workers}")

        self._num_workers = num_workers

        workstation_state = self.workstation_state
        for listener in self._workstation_state_changed_listeners:
            listener(workstation_state)
    
    @property
    def workstation_state(self) -> WorkstationState:
        sensors_active = any(s.active for s in self._sensor_system.sensors)
        if self._num_workers == 0:
            return WorkstationState.EMPTY
        elif not sensors_active:
            return WorkstationState.IDLE
        else:
            return WorkstationState.ACTIVE

    @property
    def sensors(self) -> List[Sensor]:
        return self._sensor_system.sensors

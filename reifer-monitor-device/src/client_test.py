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
from client_model import Sensor
from client_model import SensorSystem
from client_model import Device
from client_model import WorkstationState


class FakeSensorSystem(SensorSystem):
    def __init__(
            self,
            fake_sensors: List[Sensor],
            fake_sensor_change_listener: Callable[[Sensor], None]) -> None:
        self.fake_sensors = fake_sensors
        self.fake_sensor_change_listener = fake_sensor_change_listener

    @property
    def sensors(self) -> List[Sensor]:
        return self.fake_sensors

    def add_sensor_change_listener(
            self,
            listener: Callable[[Sensor], None]) -> None:
        self.fake_sensor_change_listener = listener


def test_workstation_state_empty() -> None:
    subject = Device(FakeSensorSystem([], lambda _: None))
    assert subject.workstation_state == WorkstationState.EMPTY

def test_workstation_state_idle() -> None:
    subject = Device(FakeSensorSystem([], lambda _: None))
    subject.num_workers = 1
    assert subject.workstation_state == WorkstationState.IDLE

def test_workstation_state_active() -> None:
    subject = Device(
        FakeSensorSystem(
            [Sensor(1, "Sensor", True)],
            lambda _: None))
    subject.num_workers = 1
    assert subject.workstation_state == WorkstationState.ACTIVE

def test_sensor_change_notified() -> None:
    sensors: List[Sensor] = []
    def sensors_changed(new_sensors: List[Sensor]) -> None:
        nonlocal sensors
        sensors = new_sensors
    system = FakeSensorSystem(
        [Sensor(1, "Sensor", True)],
        lambda _: None)
    subject = Device(system)
    subject.add_sensors_changed_listener(sensors_changed)
    system.fake_sensor_change_listener(Sensor(1, "Sensor", True))
    assert sensors == [Sensor(1, "Sensor", True)]

# vim: tw=80 sw=4 ts=4 expandtab:
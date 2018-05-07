from typing import Callable
from typing import List
from reifermonitor.model import Sensor
from reifermonitor.model import SensorSystem
from reifermonitor.model import Device
from reifermonitor.model import WorkstationState


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

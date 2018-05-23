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


class AmplitudeMeasurer:
    _hist: Dict[int, int]
    _quantization_factor: int
    _noise_level: int

    def __init__(self,
                 quantization_factor: int,
                 noise_level: int,
                 min_bound: int,
                 max_bound: int) -> None:
        self._hist = {}
        self._quantization_factor = quantization_factor
        self._noise_level = noise_level
        self._hist[min_bound] = 0
        self._hist[max_bound] = 0

    def sample(self, sample: int) -> None:
        quantized = sample // self._quantization_factor
        quantized *= self._quantization_factor
        self._hist[quantized] = self._hist.get(quantized, 0) + 1

    def amplitude(self) -> int:
        samples = sorted(self._hist.items(), key=itemgetter(0))
        low = None
        high = None
        previous = None
        iterator = iter(samples)
        for val, freq in iterator:
            if freq > self._noise_level:
                low = val
                break
            previous = val
        for val, freq in iterator:
            if freq <= self._noise_level:
                high = previous
                break
            previous = val
        if low is not None and high is not None:
            return high - low
        else:
            return 0


class SensorSystem(SensorSystemInterface):
    _vibration_active: bool
    _vibration_sample: bool
    _time_since_vibration_change: int
    _current_active: bool
    _current_sample_num: int
    _current_measurer: AmplitudeMeasurer
    _sensor_change_listeners: List[Callable[[Sensor], None]]
    _schedule: Tuple[Callable[[Callable[..., None]], None]]

    def __init__(self,
            schedule: Callable[[Callable[..., None]], None]) -> None:
        self._vibration_active = False
        self._vibration_sample = False
        self._time_since_vibration_change = 10000
        self._current_active = False
        self._sensor_change_listeners = []
        self._schedule = (schedule,)
        self._current_sample_num = 0
        self._current_measurer = self._new_measurer()

    def _new_measurer(self) -> AmplitudeMeasurer:
        return AmplitudeMeasurer(4, 10, 0, 4096)

    def start(self) -> None:
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(0, 0)
        schedule, = self._schedule
        schedule(self.update)

    def update(self, *args: Any) -> None:
        vibration_sample = bool(wiringpi.digitalRead(0))
        if self._vibration_sample != vibration_sample:
            self._vibration_sample = vibration_sample
            self._time_since_vibration_change = 0
        self._time_since_vibration_change += 1
        vibration_active = self._time_since_vibration_change < 1000
        if self._vibration_active != vibration_active:
            self._vibration_active = vibration_active
            for listener in self._sensor_change_listeners:
                listener(Sensor(1, "Tärinä", vibration_active))
        self._current_sample_num += 1
        if self._current_sample_num >= 1000:
            amplitude = self._current_measurer.amplitude()
            current_active = amplitude > 40
            if self._current_active != current_active:
                self._current_active = current_active
                for listener in self._sensor_change_listeners:
                    listener(Sensor(2, "Virta", current_active))
            self._current_sample_num = 0
            self._current_measurer = self._new_measurer()
        else:
            current_sample = wiringpi.analogRead(0)
            self._current_measurer.sample(current_sample)
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

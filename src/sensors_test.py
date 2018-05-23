from sensors import AmplitudeMeasurer
from typing import Any
from math import sin


def check_in_range(actual: int, expected: int) -> None:
    assert abs(actual - expected) < expected // 20


def test_amplitude_measurer() -> Any:
    for period in range(5, 150, 5):
        peak = 100
        am = AmplitudeMeasurer(4, 0, -500, 500)
        for i in range(1000):
            am.sample(int(sin(i/period) * peak))

        actual = am.amplitude()
        expected = 2 * peak
        yield check_in_range, actual, expected
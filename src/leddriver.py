# -*- coding: utf8 -*-
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

from typing import Iterator, TYPE_CHECKING, Callable, Tuple, Any

if TYPE_CHECKING:
    import fakewiringpi as wiringpi
else:
    try:
        import wiringpi
    except ImportError:
        import fakewiringpi as wiringpi

class LedDriver:
    _r: int
    _g: int
    _b: int
    _generator: Iterator[None]
    _schedule: Tuple[Callable[[Callable[..., None]], None]]

    def __init__(self,
            schedule: Callable[[Callable[..., None]], None]) -> None:
        self._r = 255
        self._g = 255
        self._b = 255
        self._generator = self._generate()
        self._schedule = (schedule,)

    def start(self) -> None:
        schedule, = self._schedule
        schedule(self.update)

    def _generate(self) -> Iterator[None]:
        while True:
            for color in (self._r, self._g, self._b):
                for i in range(8):
                    if color & (1<<i): # 1.2μs high, 1.3μs low
                        wiringpi.digitalWrite(1, 1)
                        for _ in range(12):
                            yield None
                        wiringpi.digitalWrite(1, 0)
                        for _ in range(13):
                            yield None
                    else: # 0.5μs high, 2.0μs low
                        wiringpi.digitalWrite(1, 1)
                        for _ in range(5):
                            yield None
                        wiringpi.digitalWrite(1, 0)
                        for _ in range(20):
                            yield None
            for i in range(1000): # 1000μs pause
                yield None

    def update(self, *args: Any) -> None:
        next(self._generator)
        schedule, = self._schedule
        schedule(self.update)


# vim: tw=80 sw=4 ts=4 expandtab:
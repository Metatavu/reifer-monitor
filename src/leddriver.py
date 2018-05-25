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
from threading import Thread
from time import sleep

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
    _thread: Thread

    def __init__(self) -> None:
        self._r = 255
        self._g = 255
        self._b = 255
        self._thread = Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        while True:
            for color in (self._r, self._g, self._b):
                for i in range(8):
                    if color & (1<<i): # 1.2μs high, 1.3μs low
                        wiringpi.digitalWrite(1, 1)
                        sleep(1.2e-6)
                        wiringpi.digitalWrite(1, 0)
                        sleep(1.3e-6)
                    else: # 0.5μs high, 2.0μs low
                        wiringpi.digitalWrite(1, 1)
                        sleep(0.5e-6)
                        wiringpi.digitalWrite(1, 0)
                        sleep(2.0e-6)
            sleep(1000e-6)

# vim: tw=80 sw=4 ts=4 expandtab:
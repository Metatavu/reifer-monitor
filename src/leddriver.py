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

from typing import Iterator, TYPE_CHECKING, Callable, Tuple, Any, Optional
from threading import Thread
from time import sleep
from serial import Serial
from serial.tools.list_ports import comports
from logging import log, ERROR

class LedDriver:
    _serial: Optional[Serial]

    def __init__(self) -> None:
        self._serial = None

    def start(self) -> None:
        try:
            (port, _, _), *_ = comports()
        except ValueError:
            log(ERROR, "No COM port found")
            return
        self._serial = Serial(port=port)

    def set_color(self, r: int, g: int, b: int) -> None:
        if self._serial is not None:
            self._serial.write(f"R{r}G{g}B{b}".encode('ascii'))

# vim: tw=80 sw=4 ts=4 expandtab:
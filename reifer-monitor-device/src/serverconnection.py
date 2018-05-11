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
from typing import Any
from logging import error

import zmq

from message import (BatchNameQueryRequest, BatchNameQueryResponse,
                     ErrorResponse)


class ServerError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class ServerConnection:
    def __init__(self, address: str) -> None:
        self.address = address
        self.context = zmq.Context()
        # pylint: disable=E1101
        self.socket = self.context.socket(zmq.REQ)

    def _communicate(self, message: Any) -> Any:
        self.socket.send_pyobj(message)
        result = self.socket.recv_pyobj()
        if isinstance(result, ErrorResponse):
            tb = '\n'.join(result.stack_summary.format())
            args = result.exception.args
            if len(args) == 1:
                args = (f"{args[0]}\n\n{tb}",)
            else:
                args = args + (tb,)
            result.exception.args = args
            raise result.exception
        return result

    def connect(self) -> None:
        self.socket.connect(self.address)

    def get_batch_name(self, batch_code: str) -> str:
        resp = self._communicate(BatchNameQueryRequest(batch_code))
        assert isinstance(resp, BatchNameQueryResponse)
        return resp.batch_name

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
# pylint: disable=W0614
from logging import error
from typing import Any, Optional

import zmq

from message import *


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

    def get_batch_name(self, batch_code: str) -> Optional[str]:
        resp = self._communicate(BatchNameQueryRequest(batch_code))
        assert isinstance(resp, BatchNameQueryResponse)
        return resp.batch_name

    def associate_batch(self, batch_code: str, batch_name: str) -> int:
        resp = self._communicate(BatchAssociationRequest(batch_code, batch_name))
        assert isinstance(resp, BatchAssociationResponse)
        return resp.batch_id

    def start_activity_period(self, workstation_code: str, num_workers: int) -> None:
        resp = self._communicate(
            StartActivityPeriodRequest(workstation_code, num_workers))
        assert isinstance(resp, StartActivityPeriodResponse)

    def stop_activity_period(self, workstation_code: str) -> None:
        resp = self._communicate(
            StopActivityPeriodRequest(workstation_code))
        assert isinstance(resp, StopActivityPeriodResponse)

    def start_work_run(self, workstation_code: str) -> None:
        resp = self._communicate(StartWorkRunRequest(workstation_code))
        assert isinstance(resp, StartWorkRunResponse)

    def refresh_work_run(self, workstation_code: str) -> None:
        resp = self._communicate(RefreshWorkRunRequest(workstation_code))
        assert isinstance(resp, RefreshWorkRunResponse)

    def stop_work_run(self, workstation_code: str) -> None:
        resp = self._communicate(StopWorkRunRequest(workstation_code))
        assert isinstance(resp, StopWorkRunResponse)

    def start_work(self, workstation_code: str, batch_code: str) -> None:
        resp = self._communicate(StartWorkRequest(workstation_code, batch_code))
        assert isinstance(resp, StartWorkResponse)

    def stop_work(self, workstation_code: str) -> None:
        resp = self._communicate(StopWorkRequest(workstation_code))
        assert isinstance(resp, StopWorkResponse)

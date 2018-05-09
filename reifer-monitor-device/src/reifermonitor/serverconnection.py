import zmq

from typing import Any
from reiferserver.message import BatchNameQueryRequest
from reiferserver.message import BatchNameQueryResponse
from reiferserver.message import ErrorResponse


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
            raise ServerError(f"{result.error_type}: {result.error_message}")
        return result

    def connect(self) -> None:
        self.socket.connect(self.address)

    def get_batch_name(self, batch_code: str) -> str:
        resp = self._communicate(BatchNameQueryRequest(batch_code))
        assert isinstance(resp, BatchNameQueryResponse)
        return resp.batch_name


    

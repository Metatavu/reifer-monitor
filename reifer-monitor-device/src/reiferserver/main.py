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

# pylint: disable=E1101
# THIS IS FOR PROTOTYPE USE ONLY, NO SECURITY WHATSOEVER
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Tuple
from typing import Dict
import zmq
import re
import sys
from reiferserver.message import ErrorResponse
from reiferserver.message import BatchNameQueryRequest
from reiferserver.message import BatchNameQueryResponse

class Server:
    def __init__(self, bind_address: str) -> None:
        self.bind_address = bind_address

    def run(self) -> None:
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(self.bind_address)
        
        while True:
            message = socket.recv_pyobj()
            try:
                reply = self.execute(message)
            except Exception as e:
                print(e, file=sys.stdout)
                if len(e.args) == 1:
                    msg, = e.args
                else:
                    msg = e.args
                socket.send_pyobj(ErrorResponse(str(type(e)), str(msg)))
            else:
                socket.send_pyobj(reply)

    def handle_batch_name_query(self, message: BatchNameQueryRequest):
        return BatchNameQueryResponse("Example batch")

    def execute(self, message: Any) -> Any:
        if isinstance(message, BatchNameQueryRequest):
            return self.handle_batch_name_query(message)
        else:
            return ErrorResponse("ValueError", "invalid message")


if __name__ == "__main__":
    Server("tcp://*:5555/").run()
    
# vim: tw=80 sw=4 ts=4 expandtab:
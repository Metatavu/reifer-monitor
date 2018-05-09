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
from typing import Optional
from typing import Dict
from pony import orm
import zmq
import re
import sys
import os
import toml
import yoyo
import logging
from message import ErrorResponse
from message import BatchNameQueryRequest
from message import BatchNameQueryResponse


_CONFIG: Dict[str, Any]


class ConfigurationException(Exception):
    pass


if 'REIFER_MONITOR_CONFIG' in os.environ:
    _CONFIG = toml.load(os.environ['REIFER_MONITOR_CONFIG'])
elif len(sys.argv) >= 2:
    _CONFIG = toml.load(sys.argv[1])
else:
    raise ConfigurationException(
        "Configuration file location not set. " +
        "Pass it as argv[1] or REIFER_MONITOR_CONFIG " +
        "environment variable.")


logging.basicConfig(level=getattr(logging, _CONFIG['logging_level']),
                    stream=sys.stderr,
                    format="%(asctime)s - %(module)s:%(message)s")


_DB: orm.Database = orm.Database()


class Batch(_DB.Entity): # type: ignore
    id: int = orm.PrimaryKey(int, auto=True)
    code: str = orm.Required(str, unique=True)
    name: str = orm.Required(str)

    @classmethod
    def find_by_code(cls, code: str) -> Optional[Batch]:
        with orm.db_session:
            result = cls.get(code=code)
            assert isinstance(result, (Batch, type(None)))
            return result


def run_server(bind_address: str) -> None:
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(bind_address)
    
    while True:
        message = socket.recv_pyobj()
        try:
            reply = execute(message)
        except Exception as e:
            print(e, file=sys.stdout)
            if len(e.args) == 1:
                msg, = e.args
            else:
                msg = e.args
            socket.send_pyobj(ErrorResponse(str(type(e)), str(msg)))
        else:
            socket.send_pyobj(reply)


def handle_batch_name_query(message: BatchNameQueryRequest) -> BatchNameQueryResponse:
    batch = Batch.find_by_code(message.batch_code)
    if batch is None:
        raise ValueError("batch not found")
    return BatchNameQueryResponse(batch.name)


def execute(message: Any) -> Any:
    if isinstance(message, BatchNameQueryRequest):
        return handle_batch_name_query(message)
    else:
        return ErrorResponse("ValueError", "invalid message")


def init() -> None:
    if _CONFIG["db_provider"] == 'sqlite':
        _DB.bind(provider='sqlite',
                 filename=_CONFIG["db_filename"],
                 create_db=_CONFIG["db_create"])
        migration_url = 'sqlite:///{}'.format(_CONFIG['db_filename'])
    elif _CONFIG["db_provider"] == 'postgres':
        _DB.bind(provider='postgres',
                 user=_CONFIG["db_user"],
                 password=_CONFIG["db_password"],
                 host=_CONFIG["db_host"],
                 database=_CONFIG["db_database"])
        migration_url = 'postgresql://{}:{}@{}/{}'.format(
            _CONFIG["db_user"],
            _CONFIG["db_password"],
            _CONFIG["db_host"],
            _CONFIG["db_database"])
    else:
        raise ConfigurationException("Database configured improperly")

    if _CONFIG["db_debug"]:
        orm.set_sql_debug(True)

    if _CONFIG["db_startup"] == 'make_tables':
        _DB.generate_mapping(create_tables=True)
    elif _CONFIG["db_startup"] == 'migrate':
        backend = yoyo.get_backend(migration_url)
        migrations = yoyo.read_migrations(_CONFIG['db_migrations_dir'])
        backend.apply_migrations(backend.to_apply(migrations))
        _DB.generate_mapping(create_tables=False)
    elif _CONFIG["db_startup"] == 'none':
        _DB.generate_mapping(create_tables=False)
    else:
        raise ConfigurationException("Database startup configured improperly")


if __name__ == "__main__":
    init()
    run_server(_CONFIG["bind_url"])
    

# vim: tw=80 sw=4 ts=4 expandtab:
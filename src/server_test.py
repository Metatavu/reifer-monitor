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

import server as server_module
import sys
from server import Batch, Server, init_lite
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.engine import Engine
from datetime import datetime


def session(engine: Engine) -> Session:
    sess = sessionmaker(engine)()
    assert isinstance(sess, Session)
    return sess


def test_find_batch_by_code() -> None:
    engine = init_lite("sqlite:///:memory:")
    sess = session(engine)
    created = datetime(2000, 1, 1)
    try:
        sess.execute(
            text("""INSERT INTO "Batch" ("id", "code", "name", "created") VALUES (:id,:code,:name,:created)"""),
            dict(id=1, code="CODE", name="NAME", created=created))
        sess.commit()
    finally:
        sess.close()
    server = Server(engine)
    result = server.find_batch_by_code("CODE")
    assert isinstance(result, Batch)
    assert result.id == 1
    assert result.code == "CODE"
    assert result.name == "NAME"
    assert result.created == created


def test_associate_batch_once() -> None:
    engine = init_lite("sqlite:///:memory:")
    created = datetime(2000, 1, 1)
    server_module.now = lambda: created
    server = Server(engine)
    result = server.associate_batch("CODE", "NAME")
    assert isinstance(result, Batch)
    assert result.id == 1
    assert result.code == "CODE"
    assert result.name == "NAME"
    assert result.created == created


def test_associate_batch_twice() -> None:
    engine = init_lite("sqlite:///:memory:")
    created = datetime(2000, 1, 1)
    server_module.now = lambda: created
    server = Server(engine)
    result = server.associate_batch("CODE", "ORIG")
    assert isinstance(result, Batch)
    assert result.id == 1
    assert result.code == "CODE"
    assert result.name == "ORIG"
    assert result.created == created
    result2 = server.associate_batch("CODE", "NEW")
    assert isinstance(result2, Batch)
    assert result2.id == 2
    assert result2.code == "CODE"
    assert result2.name == "NEW"
    assert result2.created == created
    sess = session(engine)
    try:
        rows = sess.execute(
            text("""SELECT "id", "code", "name", "created" FROM "Batch"
                    WHERE "id" = :id"""),
            dict(id=1)
            ).fetchall()
    finally:
        sess.close()
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["code"] == None
    assert rows[0]["name"] == "ORIG"
    assert rows[0]["created"] == '2000-01-01 00:00:00.000000'


def test_start_activity_period() -> None:
    engine = init_lite("sqlite:///:memory:")
    started = datetime(2000, 1, 1)
    server_module.now = lambda: started
    server = Server(engine)
    server.start_activity_period("WS1", 1)
    sess = session(engine)
    try:
        rows = sess.execute(
            text("""SELECT "id", "workstation_id", "num_workers", "start", "stop"
                    FROM "ActivityPeriod" """)
            ).fetchall()
    finally:
        sess.close()
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["workstation_id"] == 1
    assert rows[0]["num_workers"] == 1
    assert rows[0]["start"] == '2000-01-01 00:00:00.000000'
    assert rows[0]["stop"] == None


def test_start_stop_activity_period() -> None:
    engine = init_lite("sqlite:///:memory:")
    started = datetime(2000, 1, 1)
    server_module.now = lambda: started
    server = Server(engine)
    server.start_activity_period("WS1", 1)
    stopped = datetime(2000, 1, 2)
    server_module.now = lambda: stopped
    server.stop_activity_period("WS1")
    sess = session(engine)
    try:
        rows = sess.execute(
            text("""SELECT "id", "workstation_id", "num_workers", "start", "stop"
                    FROM "ActivityPeriod" """)
            ).fetchall()
    finally:
        sess.close()
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["workstation_id"] == 1
    assert rows[0]["num_workers"] == 1
    assert rows[0]["start"] == '2000-01-01 00:00:00.000000'
    assert rows[0]["stop"] == '2000-01-02 00:00:00.000000'


# vim: tw=80 sw=4 ts=4 expandtab:
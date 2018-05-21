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
# pylint: disable=E1101,E0601,W0614
# THIS IS FOR PROTOTYPE USE ONLY, NO SECURITY WHATSOEVER

import logging
import logging.config
import os
import re
import sys
from abc import ABCMeta, abstractmethod
from datetime import datetime
from traceback import extract_tb
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, List

import toml
import yoyo
import zmq
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        create_engine, desc)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.exc import DBAPIError

from message import *


class ConfigurationException(Exception):
    pass


if TYPE_CHECKING:
    class BaseEntity:
        metadata: Any
        def __init__(self, **kwargs: Any) -> None:
            pass
else:
    BaseEntity = declarative_base()


def now() -> datetime:
    return datetime.now()


class Workstation(BaseEntity):
    __tablename__: str = "Workstation"
    id: int = Column(Integer, primary_key=True)
    code: str = Column(String(255), unique=True, nullable=False)

    def __init__(self, code: str) -> None:
        super().__init__(code=code)


class Batch(BaseEntity):
    __tablename__: str = "Batch"
    id: int = Column(Integer, primary_key=True)
    code: Optional[str] = Column(String(255), unique=True)
    name: str = Column(String(255), nullable=False)
    created: datetime = Column(DateTime, nullable=False)

    def __init__(self, code: Optional[str], name: str) -> None:
        super().__init__(code=code,
                         name=name,
                         created=now())


class ActivityPeriod(BaseEntity):
    __tablename__: str = "ActivityPeriod"
    id: int = Column(Integer, primary_key=True)
    workstation_id: int = Column(Integer, ForeignKey("Workstation.id"))
    workstation: Workstation = relationship("Workstation")
    num_workers: int = Column(Integer, nullable=False)
    start: datetime = Column(DateTime, nullable=False)
    stop: Optional[datetime] = Column(DateTime, nullable=True)

    def __init__(self,
                 workstation: Workstation,
                 num_workers: int) -> None:
        super().__init__(
            workstation_id=workstation.id,
            num_workers=num_workers,
            start=now(),
            stop=None)


class WorkRun(BaseEntity):
    __tablename__: str = "WorkRun"
    id: int = Column(Integer, primary_key=True)
    workstation_id: int = Column(Integer, ForeignKey("Workstation.id"))
    workstation: Workstation = relationship("Workstation")
    batch_id: Optional[int] = Column(Integer, ForeignKey("Batch.id"), nullable=True)
    batch: Optional[Batch] = relationship("Batch")
    start: datetime = Column(DateTime, nullable=False)
    stop: Optional[datetime] = Column(DateTime, nullable=True)

    def __init__(self,
                 workstation: Workstation,
                 batch: Optional[Batch]) -> None:
        super().__init__(
            workstation_id=workstation.id,
            batch_id=batch.id if batch is not None else None,
            start=now(),
            stop=None)


class Work(BaseEntity):
    __tablename__: str = "Work"
    id: int = Column(Integer, primary_key=True)
    workstation_id: int = Column(Integer, ForeignKey("Workstation.id"))
    workstation: Workstation = relationship("Workstation")
    batch_id: int = Column(Integer, ForeignKey("Batch.id"), nullable=False)
    batch: Batch = relationship("Batch")
    start: datetime = Column(DateTime, nullable=False)
    stop: Optional[datetime] = Column(DateTime, nullable=True)

    def __init__(self,
                 workstation: Workstation,
                 batch: Batch) -> None:
        super().__init__(
            workstation_id=workstation.id,
            batch_id=batch.id,
            start=now(),
            stop=None)


def bind_tables(engine: Engine) -> None:
    Workstation.metadata.bind = engine
    ActivityPeriod.metadata.bind = engine
    WorkRun.metadata.bind = engine
    Work.metadata.bind = engine
    Batch.metadata.bind = engine


class Server:
    engine: Engine
    sessionmaker: Callable[[], Session]

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.make_session = sessionmaker(bind=engine)

    def session(self) -> Session:
        return self.make_session()

    def find_batch_by_code(self, code: str) -> Optional[Batch]:
        sess = self.session()
        try:
            batch = sess.query(Batch).filter_by(code=code).first()
            assert isinstance(batch, (Batch, type(None)))
            return batch
        finally:
            sess.close()

    def associate_batch(self, code: str, name: str) -> Batch:
        sess = self.session()
        try:
            old_batch = sess.query(Batch).filter_by(code=code).first()
            if isinstance(old_batch, Batch):
                old_batch.code = None
            new_batch = Batch(code, name)
            sess.add(new_batch)
            sess.commit()
            sess.refresh(new_batch)
            return new_batch
        finally:
            sess.close()

    def ensure_workstation(self, workstation_code: str) -> None:
        sess = self.session()
        try:
            ws = Workstation(workstation_code)
            sess.add(ws)
            sess.commit()
        except DBAPIError:
            pass
        finally:
            sess.close()

    def find_workstation_by_code(self,
                                 sess: Session,
                                 workstation_code: str) -> Workstation:
        ws = sess.query(Workstation).filter_by(code=workstation_code).one()
        assert isinstance(ws, Workstation)
        return ws

    def start_activity_period(self,
                              workstation_code: str,
                              num_workers: int) -> None:
        self.ensure_workstation(workstation_code)
        print(f"Starting activity period on {workstation_code} " +
              f"with {num_workers} workers")
        sess = self.session()
        try:
            ws = self.find_workstation_by_code(sess, workstation_code)
            ap = ActivityPeriod(ws, num_workers)
            sess.add(ap)
            sess.commit()
        finally:
            sess.close()

    def stop_activity_period(self,
                             workstation_code: str) -> None:
        self.ensure_workstation(workstation_code)
        print(f"Stopping activity period on {workstation_code}")
        sess = self.session()
        try:
            ws = self.find_workstation_by_code(sess, workstation_code)
            ap = (sess.query(ActivityPeriod)
                      .filter_by(workstation_id=ws.id)
                      .order_by(desc(ActivityPeriod.start))
                      .first())
            if ap is None:
                return
            assert isinstance(ap, ActivityPeriod)
            ap.stop = now()
            sess.add(ap)
            sess.commit()
        finally:
            sess.close()

    def start_work_run(self,
                       workstation_code: str) -> None:
        self.ensure_workstation(workstation_code)
        print(f"Starting work run on {workstation_code}")
        sess = self.session()
        try:
            ws = self.find_workstation_by_code(sess, workstation_code)
            work = (sess.query(Work)
                      .filter_by(workstation_id=ws.id)
                      .order_by(desc(Work.start))
                      .first())
            if work is None:
                run = WorkRun(ws, None)
            else:
                run = WorkRun(ws, work.batch)
            sess.add(run)
            sess.commit()
        finally:
            sess.close()

    def stop_work_run(self,
                      workstation_code: str) -> None:
        self.ensure_workstation(workstation_code)
        print(f"Stopping work run on {workstation_code}")
        sess = self.session()
        try:
            ws = self.find_workstation_by_code(sess, workstation_code)
            run = (sess.query(WorkRun)
                      .filter_by(workstation_id=ws.id)
                      .order_by(desc(WorkRun.start))
                      .first())
            if run is None:
                return
            assert isinstance(run, WorkRun)
            run.stop = now()
            sess.add(run)
            sess.commit()
        finally:
            sess.close()

    def start_work(self,
                   workstation_code: str,
                   batch_code: str) -> None:
        self.ensure_workstation(workstation_code)
        batch = self.find_batch_by_code(batch_code)
        if batch is None:
            raise ValueError("Batch doesn't exist")
        print(f"Starting work on {workstation_code} for {batch_code}")
        sess = self.session()
        try:
            ws = self.find_workstation_by_code(sess, workstation_code)
            work = Work(ws, batch)
            sess.add(work)
            sess.commit()
        finally:
            sess.close()

    def stop_work(self,
                  workstation_code: str) -> None:
        self.ensure_workstation(workstation_code)
        print(f"Stopping work on {workstation_code}")
        sess = self.session()
        try:
            ws = self.find_workstation_by_code(sess, workstation_code)
            work = (sess.query(Work)
                      .filter_by(workstation_id=ws.id)
                      .order_by(desc(Work.start))
                      .first())
            if work is None:
                return
            assert isinstance(work, Work)
            work.stop = now()
            sess.add(work)
            sess.commit()
        finally:
            sess.close()

    def run_server(self, bind_address: str) -> None:
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(bind_address)

        print("server started")
        
        while True:
            message = socket.recv_pyobj()
            try:
                reply = self.execute(message)
            except Exception as e:
                tb = extract_tb(sys.exc_info()[2])
                socket.send_pyobj(ErrorResponse(e, tb))
            else:
                socket.send_pyobj(reply)

    def handle_batch_name_query(self, message: BatchNameQueryRequest) -> BatchNameQueryResponse:
        batch = self.find_batch_by_code(message.batch_code)
        if batch is None:
            raise ValueError("batch not found")
        return BatchNameQueryResponse(batch.name)

    def handle_batch_association(self, message: BatchAssociationRequest) -> BatchAssociationResponse:
        batch = self.associate_batch(message.batch_code, message.batch_name)
        return BatchAssociationResponse(batch.id)

    def handle_start_activity_period(self, message: StartActivityPeriodRequest) -> StartActivityPeriodResponse:
        self.start_activity_period(message.workstation_code, message.num_workers)
        return StartActivityPeriodResponse()

    def handle_stop_activity_period(self, message: StopActivityPeriodRequest) -> StopActivityPeriodResponse:
        self.stop_activity_period(message.workstation_code)
        return StopActivityPeriodResponse()

    def handle_start_work_run(self, message: StartWorkRunRequest) -> StartWorkRunResponse:
        self.start_work_run(message.workstation_code)
        return StartWorkRunResponse()

    def handle_stop_work_run(self, message: StopWorkRunRequest) -> StopWorkRunResponse:
        self.stop_work_run(message.workstation_code)
        return StopWorkRunResponse()

    def handle_start_work(self, message: StartWorkRequest) -> StartWorkResponse:
        self.start_work(message.workstation_code, message.batch_code)
        return StartWorkResponse()

    def handle_stop_work(self, message: StopWorkRequest) -> StopWorkResponse:
        self.stop_work(message.workstation_code)
        return StopWorkResponse()

    def execute(self, message: Any) -> Any:
        if isinstance(message, BatchNameQueryRequest):
            return self.handle_batch_name_query(message)
        if isinstance(message, BatchAssociationRequest):
            return self.handle_batch_association(message)
        if isinstance(message, StartActivityPeriodRequest):
            return self.handle_start_activity_period(message)
        if isinstance(message, StopActivityPeriodRequest):
            return self.handle_stop_activity_period(message)
        if isinstance(message, StartWorkRunRequest):
            return self.handle_start_work_run(message)
        if isinstance(message, StopWorkRunRequest):
            return self.handle_stop_work_run(message)
        if isinstance(message, StartWorkRequest):
            return self.handle_start_work(message)
        if isinstance(message, StopWorkRequest):
            return self.handle_stop_work(message)
        else:
            raise ValueError("invalid message")


def make_config() -> Dict[str, Any]:
    if 'REIFER_MONITOR_CONFIG' in os.environ:
        conf = toml.load(os.environ['REIFER_MONITOR_CONFIG'])
        assert isinstance(conf, dict)
        return conf
    elif len(sys.argv) >= 2:
        conf = toml.load(sys.argv[1])
        assert isinstance(conf, dict)
        return conf
    else:
        raise ConfigurationException(
            "Configuration file location not set. " +
            "Pass it as argv[1] or REIFER_MONITOR_CONFIG " +
            "environment variable.")


def init_lite(url: str) -> Engine:
    engine = create_engine(url)
    BaseEntity.metadata.create_all(engine)
    bind_tables(engine)
    return engine


def init(config: Dict[str, Any]) -> Engine:
    logging.basicConfig(level=getattr(logging, config['logging_level']),
                        stream=sys.stderr,
                        format="%(asctime)s - %(module)s:%(message)s")

    if config["db_provider"] == 'sqlite':
        url = 'sqlite:///{}'.format(config['db_filename'])
    elif config["db_provider"] == 'postgres':
        url = 'postgresql://{}:{}@{}/{}'.format(
            config["db_user"],
            config["db_password"],
            config["db_host"],
            config["db_database"])
    else:
        raise ConfigurationException("Database configured improperly")

    engine = create_engine(url)
    migration_url = url

    if config["db_startup"] == 'make_tables':
        BaseEntity.metadata.create_all(engine)
        bind_tables(engine)
    elif config["db_startup"] == 'migrate':
        backend = yoyo.get_backend(migration_url)
        migrations = yoyo.read_migrations(config['db_migrations_dir'])
        backend.apply_migrations(backend.to_apply(migrations))
        bind_tables(engine)
    elif config["db_startup"] == 'none':
        bind_tables(engine)
    else:
        raise ConfigurationException("Database startup configured improperly")
        
    return engine


if __name__ == "__main__":
    print("starting server...")
    config = make_config()
    engine = init(config)
    Server(engine).run_server(config["bind_url"])

# vim: tw=80 sw=4 ts=4 expandtab:

"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session
from settings import env_data
from contextlib import contextmanager


class Engine:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not Engine._initialized:
            # check_same_thread=False is required for SQLite when background
            # threads (e.g. OfficePushWorker) share the same engine singleton.
            # timeout=30 prevents instant "database is locked" errors under
            # brief write contention from concurrent sessions.
            connect_args: dict = {}
            db_url = f"{env_data.db_engine}:///{env_data.db_name}"
            if env_data.db_engine == "sqlite":
                connect_args = {"check_same_thread": False, "timeout": 30}

            self.engine = create_engine(
                db_url,
                pool_size=5,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args=connect_args,
                echo=False,
            )

            # expire_on_commit=False keeps ORM objects readable after commit,
            # which is important for objects passed between sessions.
            self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

            Engine._initialized = True

    @contextmanager
    def get_session(self):
        """Context manager for safe session management"""
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @property 
    def session(self):
        """For backward compatibility - however get_session() is recommended"""
        if not hasattr(self, '_session') or self._session is None:
            self._session = self.SessionFactory()
        return self._session
    
    def close_session(self):
        """Safely close current session"""
        if hasattr(self, '_session') and self._session:
            self._session.close()
            self._session = None
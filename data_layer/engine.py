"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
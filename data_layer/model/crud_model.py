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

from sqlalchemy.orm import declarative_base
from sqlalchemy import func, desc, asc, update as sql_update, inspect as sa_inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from uuid import uuid4

from data_layer.engine import Engine
from core.exceptions import DatabaseError



from core.logger import get_logger

logger = get_logger(__name__)
Model = declarative_base()
metadata = Model.metadata


class CRUD:
    """
    Base class for performing Create, Read, Update, Delete operations
    """
    
    def __init__(self):
        self._engine = Engine()
    
    def _get_engine(self):
        """
        Get engine instance, creating it if it doesn't exist.
        This allows models loaded from database (where __init__ wasn't called) to work.
        """
        if not hasattr(self, '_engine') or self._engine is None:
            self._engine = Engine()
        return self._engine

    # CREATE Operations
    def save(self) -> bool:
        """
        Saves record to database: UPDATE if exists (by PK), INSERT if not.

        Uses an explicit UPDATE-then-INSERT strategy instead of session.merge(),
        which can silently try INSERT for detached objects when the SQLAlchemy
        identity map cannot match the UUID format stored in SQLite TEXT columns.
        """
        try:
            engine = self._get_engine()
            with engine.get_session() as session:
                if hasattr(self, 'id') and self.id is None:
                    self.id = uuid4()

                # Build a dict of all non-PK column values for the UPDATE
                try:
                    mapper = sa_inspect(type(self))
                    update_dict = {
                        col.key: getattr(self, col.key)
                        for col in mapper.column_attrs
                        if col.key != 'id' and hasattr(self, col.key)
                    }
                except Exception:
                    update_dict = {}

                if update_dict and hasattr(self, 'id') and self.id is not None:
                    # Try UPDATE first
                    result = session.execute(
                        sql_update(type(self))
                        .where(type(self).id == self.id)
                        .values(**update_dict)
                    )
                    session.flush()
                    if result.rowcount == 0:
                        # Record not in DB yet — INSERT it
                        session.add(self)
                else:
                    session.add(self)

                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error("Save operation error: %s", e)
            raise DatabaseError(f"Save operation failed: {e}") from e

    def create(self) -> bool:
        """
        Creates a new record.
        Works even if model was loaded from database (lazy engine initialization).
        """
        try:
            engine = self._get_engine()
            with engine.get_session() as session:
                if hasattr(self, 'id') and self.id is None:
                    self.id = uuid4()
                session.add(self)
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error("Create operation error: %s", e)
            raise DatabaseError(f"Create operation failed: {e}") from e

    # READ Operations
    @classmethod
    def get_by_id(cls, record_id) -> Optional['CRUD']:
        """
        Returns single record by ID
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                return session.query(cls).filter(cls.id == record_id).first()
        except SQLAlchemyError as e:
            logger.error("Get by ID operation error: %s", e)
            raise DatabaseError(f"Get by ID operation failed: {e}") from e

    @classmethod
    def get_all(cls, is_deleted: bool = False) -> List['CRUD']:
        """
        Returns all records
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                query = session.query(cls)
                
                # Filter by is_deleted field if it exists
                if hasattr(cls, 'is_deleted'):
                    query = query.filter(cls.is_deleted == is_deleted)
                
                return query.all()
        except SQLAlchemyError as e:
            logger.error("Get all operation error: %s", e)
            raise DatabaseError(f"Get all operation failed: {e}") from e

    @classmethod
    def filter_by(cls, **kwargs) -> List['CRUD']:
        """
        Filters records by specified criteria
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                query = session.query(cls)
                
                for key, value in kwargs.items():
                    if hasattr(cls, key):
                        query = query.filter(getattr(cls, key) == value)
                
                return query.all()
        except SQLAlchemyError as e:
            logger.error("Filter by operation error: %s", e)
            raise DatabaseError(f"Filter by operation failed: {e}") from e

    @classmethod
    def find_first(cls, **kwargs) -> Optional['CRUD']:
        """
        Returns first record matching criteria
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                query = session.query(cls)
                
                for key, value in kwargs.items():
                    if hasattr(cls, key):
                        query = query.filter(getattr(cls, key) == value)
                
                return query.first()
        except SQLAlchemyError as e:
            logger.error("Find first operation error: %s", e)
            raise DatabaseError(f"Find first operation failed: {e}") from e

    @classmethod
    def count(cls, **kwargs) -> int:
        """
        Returns count of records matching criteria
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                query = session.query(cls)
                
                for key, value in kwargs.items():
                    if hasattr(cls, key):
                        query = query.filter(getattr(cls, key) == value)
                
                return query.count()
        except SQLAlchemyError as e:
            logger.error("Count operation error: %s", e)
            raise DatabaseError(f"Count operation failed: {e}") from e

    @classmethod
    def paginate(cls, page: int = 1, per_page: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Returns paginated records
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                query = session.query(cls)
                
                # Filtering
                for key, value in kwargs.items():
                    if hasattr(cls, key):
                        query = query.filter(getattr(cls, key) == value)
                
                # Total record count
                total = query.count()
                
                # Pagination
                offset = (page - 1) * per_page
                items = query.offset(offset).limit(per_page).all()
                
                return {
                    'items': items,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
        except SQLAlchemyError as e:
            logger.error("Paginate operation error: %s", e)
            raise DatabaseError(f"Paginate operation failed: {e}") from e

    # UPDATE Operations
    def update(self, **kwargs) -> bool:
        """
        Updates current record.
        Works even if model was loaded from database (lazy engine initialization).
        """
        try:
            engine = self._get_engine()
            with engine.get_session() as session:
                # Update current object
                for key, value in kwargs.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                # Update updated_at field if exists
                if hasattr(self, 'updated_at'):
                    self.updated_at = func.now()
                
                session.merge(self)
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error("Update operation error: %s", e)
            raise DatabaseError(f"Update operation failed: {e}") from e

    @classmethod
    def update_by_id(cls, record_id, **kwargs) -> bool:
        """
        Updates record by ID
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                # Add updated_at if field exists
                if hasattr(cls, 'updated_at'):
                    kwargs['updated_at'] = func.now()
                
                result = session.query(cls).filter(cls.id == record_id).update(kwargs)
                return result > 0
        except SQLAlchemyError as e:
            logger.error("Update by ID operation error: %s", e)
            raise DatabaseError(f"Update by ID operation failed: {e}") from e

    # DELETE Operations
    def delete(self, soft_delete: bool = True) -> bool:
        """
        Deletes record (soft delete or hard delete).
        Works even if model was loaded from database (lazy engine initialization).
        """
        try:
            engine = self._get_engine()
            with engine.get_session() as session:
                if soft_delete and hasattr(self, 'is_deleted'):
                    # Soft delete
                    self.is_deleted = True
                    if hasattr(self, 'updated_at'):
                        self.updated_at = func.now()
                    session.merge(self)
                else:
                    # Hard delete
                    session.delete(self)
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error("Delete operation error: %s", e)
            raise DatabaseError(f"Delete operation failed: {e}") from e

    @classmethod
    def delete_by_id(cls, record_id, soft_delete: bool = True) -> bool:
        """
        Deletes record by ID
        """
        try:
            engine = Engine()
            with engine.get_session() as session:
                record = session.query(cls).filter(cls.id == record_id).first()
                if record:
                    if soft_delete and hasattr(cls, 'is_deleted'):
                        # Soft delete
                        update_data = {'is_deleted': True}
                        if hasattr(cls, 'updated_at'):
                            update_data['updated_at'] = func.now()
                        session.query(cls).filter(cls.id == record_id).update(update_data)
                    else:
                        # Hard delete
                        session.delete(record)
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error("Delete by ID operation error: %s", e)
            raise DatabaseError(f"Delete by ID operation failed: {e}") from e

    def restore(self) -> bool:
        """
        Restores soft deleted record
        """
        if hasattr(self, 'is_deleted'):
            return self.update(is_deleted=False)
        return False

    # Utility Operations
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts model object to dictionary
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if hasattr(value, 'isoformat'):  # Convert DateTime objects to string
                value = value.isoformat()
            elif hasattr(value, '__str__') and not isinstance(value, (int, float, bool)):
                value = str(value)
            result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CRUD':
        """
        Creates model object from dictionary
        """
        # Remove ID from data (will be auto-assigned)
        if 'id' in data:
            del data['id']
        
        return cls(**data)

    def refresh(self) -> bool:
        """
        Reloads current data from database.
        Works even if model was loaded from database (lazy engine initialization).
        """
        try:
            engine = self._get_engine()
            with engine.get_session() as session:
                session.refresh(self)
                return True
        except SQLAlchemyError as e:
            logger.error("Refresh operation error: %s", e)
            raise DatabaseError(f"Refresh operation failed: {e}") from e

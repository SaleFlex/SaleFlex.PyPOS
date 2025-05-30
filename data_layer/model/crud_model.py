"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi (ferhat.mousavi@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import func, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from uuid import uuid4

from data_layer.engine import Engine


Model = declarative_base()
metadata = Model.metadata


class CRUD:
    """
    Base class for performing Create, Read, Update, Delete operations
    """
    
    def __init__(self):
        self._engine = Engine()

    # CREATE Operations
    def save(self) -> bool:
        """
        Saves record to database, inserts if new, updates if exists
        """
        try:
            with self._engine.get_session() as session:
                # If no ID, assign a new UUID (for UUID-enabled models)
                if hasattr(self, 'id') and self.id is None:
                    self.id = uuid4()
                
                session.merge(self)  # merge handles both insert and update
                return True
        except SQLAlchemyError as e:
            print(f"Save operation error: {e}")
            return False

    def create(self) -> bool:
        """
        Creates a new record
        """
        try:
            with self._engine.get_session() as session:
                if hasattr(self, 'id') and self.id is None:
                    self.id = uuid4()
                session.add(self)
                return True
        except SQLAlchemyError as e:
            print(f"Create operation error: {e}")
            return False

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
            print(f"Get by ID operation error: {e}")
            return None

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
            print(f"Get all operation error: {e}")
            return []

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
            print(f"Filter by operation error: {e}")
            return []

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
            print(f"Find first operation error: {e}")
            return None

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
            print(f"Count operation error: {e}")
            return 0

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
            print(f"Paginate operation error: {e}")
            return {'items': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}

    # UPDATE Operations
    def update(self, **kwargs) -> bool:
        """
        Updates current record
        """
        try:
            with self._engine.get_session() as session:
                # Update current object
                for key, value in kwargs.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                # Update updated_at field if exists
                if hasattr(self, 'updated_at'):
                    self.updated_at = func.now()
                
                session.merge(self)
                return True
        except SQLAlchemyError as e:
            print(f"Update operation error: {e}")
            return False

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
            print(f"Update by ID operation error: {e}")
            return False

    # DELETE Operations
    def delete(self, soft_delete: bool = True) -> bool:
        """
        Deletes record (soft delete or hard delete)
        """
        try:
            with self._engine.get_session() as session:
                if soft_delete and hasattr(self, 'is_deleted'):
                    # Soft delete
                    self.is_deleted = True
                    if hasattr(self, 'updated_at'):
                        self.updated_at = func.now()
                    session.merge(self)
                else:
                    # Hard delete
                    session.delete(self)
                return True
        except SQLAlchemyError as e:
            print(f"Delete operation error: {e}")
            return False

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
            print(f"Delete by ID operation error: {e}")
            return False

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
        Reloads current data from database
        """
        try:
            with self._engine.get_session() as session:
                session.refresh(self)
                return True
        except SQLAlchemyError as e:
            print(f"Refresh operation error: {e}")
            return False

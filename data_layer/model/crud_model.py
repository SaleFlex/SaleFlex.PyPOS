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
from sqlalchemy import func

from data_layer.engine import Engine


Model = declarative_base()
metadata = Model.metadata


class CRUD:
    def __init__(self):
        self.engine = Engine()

    def filter_by(self, *args, **kwargs):
        return self.engine.session.query(type(self)).filter_by(*args, **kwargs)

    def save(self):
        if self.id is None:
            self.id = self.engine.session.query(func.max(type(self).id)).scalar() or 1
        self.engine.session.add(self)
        return self.engine.session.commit()

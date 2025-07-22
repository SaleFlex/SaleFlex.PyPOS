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

from data_layer.data import FormName
from pos.data import DocumentState, DocumentType, DocumentResult


class CurrentStatus:
    def __init__(self):
        self.__login_succeed = False
        self.__previous_form_type = FormName.NONE
        self.__current_form_type = FormName.LOGIN     # initial form
        self.__document_state = DocumentState.NONE
        self.__document_type = DocumentType.NONE
        self.__document_result = DocumentResult.NONE

    @property
    def login_succeed(self):
        return self.__login_succeed

    @login_succeed.setter
    def login_succeed(self, value):
        self.__login_succeed = value

    @property
    def current_form_type(self):
        return self.__current_form_type

    @current_form_type.setter
    def current_form_type(self, value):
        self.__previous_form_type = self.__current_form_type
        self.__current_form_type = value

    @property
    def previous_form_type(self):
        return self.__previous_form_type

    @previous_form_type.setter
    def previous_form_type(self, value):
        self.__previous_form_type = value

    @property
    def document_state(self):
        return self.__document_state

    @document_state.setter
    def document_state(self, value):
        self.__document_state = value

    @property
    def document_type(self):
        return self.__document_type

    @document_type.setter
    def document_type(self, value):
        self.__document_type = value

    @property
    def document_result(self):
        return self.__document_result

    @document_result.setter
    def document_result(self, value):
        self.__document_result = value

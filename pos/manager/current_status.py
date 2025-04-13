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

from pos.data import DisplayType, DocumentState, DocumentType, DocumentResult


class CurrentStatus:
    def __init__(self):
        self.__login_succeed = False
        self.__previous_display_type = DisplayType.NONE
        self.__current_display_type = DisplayType.LOGIN     # initial display
        self.__document_state = DocumentState.NONE
        self.__document_type = DocumentType.NONE
        self.__document_result = DocumentResult.NONE

    @property
    def login_succeed(self):
        return self.__login_succeed

    @login_succeed.setter
    def login_succeed(self, value):
        if type(value) is bool:
            self.__login_succeed = value

    @property
    def current_display_type(self):
        return self.__current_display_type

    @current_display_type.setter
    def current_display_type(self, value):
        self.__previous_display_type = self.__current_display_type
        if value != DisplayType.LOGIN and self.__login_succeed is False:
            self.__current_display_type = DisplayType.LOGIN
        elif type(value) is DisplayType:
            self.__current_display_type = value

    @property
    def previous_display_type(self):
        return self.__previous_display_type

    @previous_display_type.setter
    def previous_display_type(self, value):
        self.__previous_display_type = value

    @property
    def document_state(self):
        return self.__document_state

    @document_state.setter
    def document_state(self, value):
        if type(value) is DocumentState:
            self.__document_state = value

    @property
    def document_type(self):
        return self.__document_type

    @document_type.setter
    def document_type(self, value):
        if type(value) is DocumentType:
            self.__document_type = value

    @property
    def document_result(self):
        return self.__document_result

    @document_result.setter
    def document_result(self, value):
        if type(value) is DocumentResult:
            self.__document_result = value

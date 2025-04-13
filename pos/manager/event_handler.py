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
from pos.data import EventName
from pos.manager.event import GeneralEvent, ReportEvent, SaleEvent, ConfigurationEvent


class EventHandler(GeneralEvent, ReportEvent, SaleEvent, ConfigurationEvent):
    def event_distributor(self, event_name):
        function_object = None
        match event_name:
            case EventName.NONE.name:
                pass
            case EventName.EXIT_APPLICATION.name:
                function_object = self._exit_application
            case EventName.LOGIN.name:
                function_object = self._login
            case EventName.LOGOUT.name:
                function_object = self._logout
            case EventName.SALE.name:
                function_object = self._sale
            case EventName.CONFIG.name:
                function_object = self._configuration
            case EventName.CLOSURE.name:
                function_object = self._closure
            case EventName.BACK.name:
                function_object = self._back
        return function_object

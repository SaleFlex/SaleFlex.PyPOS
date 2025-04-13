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

import tomllib

from pos.data import DisplayType
from settings import env_data


class Interpreter:
    __instance = None
    __display_type = None

    def __new__(cls, display_type: DisplayType, *args, **kwargs):
        if cls.__instance is None or cls.__display_type is not display_type:
            cls.__instance = super().__new__(cls)
            cls.__display_type = display_type
        return cls.__instance

    def __init__(self, display_type: DisplayType):
        self.__display_type = display_type
        self.__toml_file_name = self.__set_toml_file_name()
        self.__design_file_data = {}
        
        try:
            with open(self.__toml_file_name, "rb") as file_object:
                self.__design_file_data = tomllib.load(file_object)
        except FileNotFoundError:
            print(f"Design file not found: {self.__toml_file_name}")
            try:
                # Fallback to default.toml if available
                with open("design_files/default.toml", "rb") as file_object:
                    self.__design_file_data = tomllib.load(file_object)
            except FileNotFoundError:
                print("Default design file not found. Using built-in defaults.")
        except tomllib.TOMLDecodeError as e:
            print(f"Error parsing design file {self.__toml_file_name}: {e}")

    @property
    def settings(self):
        settings_data = self.__design_file_data.get("settings")
        if settings_data:
            return settings_data
        return {'name': 'SaleFlex',
                'functionality': 'NONE',
                'login_required': False,
                'toolbar': False,
                'statusbar': False,
                'background_color': 0xFFFFFF,
                'foreground_color': 0x000000,
                'width': 1280,
                'height': 640}

    @property
    def toolbar_settings(self):
        design_data = self.__design_file_data.get("toolbar_settings")
        return design_data

    @property
    def design(self):
        design_data = self.__design_file_data.get("design")
        return design_data

    def __set_toml_file_name(self):
        toml_file_name = "design_files/default.toml"
        try:
            match self.__display_type:
                case DisplayType.LOGIN:
                    if 'login' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['login']}"
                case DisplayType.MENU:
                    if 'menu' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['menu']}"
                case DisplayType.SALE:
                    if 'sale' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['sale']}"
                case DisplayType.SERVICE:
                    if 'service' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['service']}"
                case DisplayType.CONFIG:
                    if 'config' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['config']}"
                case DisplayType.PARAMETER:
                    if 'parameter' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['parameter']}"
                case DisplayType.REPORT:
                    if 'report' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['report']}"
                case DisplayType.FUNCTION:
                    if 'function' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['function']}"
                case DisplayType.CUSTOMER:
                    if 'customer' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['customer']}"
                case DisplayType.VOID:
                    if 'void' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['void']}"
                case DisplayType.REFUND:
                    if 'refund' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['refund']}"
                case DisplayType.STOCK:
                    if 'stock' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['stock']}"
                case DisplayType.CLOSURE:
                    if 'closure' in env_data.main_display_data:
                        toml_file_name = f"design_files/{env_data.main_display_data['closure']}"
        except (AttributeError, TypeError, KeyError) as e:
            print(f"Error loading design file: {e}")
            
        return toml_file_name

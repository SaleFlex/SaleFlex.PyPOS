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

import os
import sys
import tomllib


class Settings:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        with open("settings.toml", "rb") as file_object:
            self.setting_data = tomllib.load(file_object)
            self.app = self.setting_data.get("app")
            self.database = self.setting_data.get("database")
            self.main_display = self.setting_data.get("main_display")
            self.customer_display = self.setting_data.get("customer_display")
            self.design_files_list = self.setting_data.get("design_files")

    @property
    def db_engine(self):
        if self.database:
            return self.database.get("engine")
        return None

    @property
    def db_name(self):
        if self.database:
            return self.database.get("database_name")
        return None

    @property
    def md_width(self):
        if self.main_display:
            return self.main_display.get("width")
        return 1280

    @property
    def md_height(self):
        if self.main_display:
            return self.main_display.get("height")
        return 640

    @property
    def cd_width(self):
        if self.customer_display:
            return self.customer_display.get("width")
        return 1280

    @property
    def cd_height(self):
        if self.customer_display:
            return self.customer_display.get("height")
        return 640

    @property
    def main_display_data(self):
        if self.design_files_list["main_display"]:
            return self.design_files_list["main_display"]
        return None

    @property
    def customer_display_data(self):
        if self.design_files_list["customer_display"]:
            return self.design_files_list["customer_display"]
        return None

    @property
    def image_absolute_folder(self):
        project_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        image_path = os.path.join(project_path, 'design_files', 'images')
        return image_path

    @property
    def app_version(self):
        """Return application version from settings.toml, or empty string if missing.

        Looks for these keys in order:
        - app.version
        - application.version
        - version (top-level)
        - app_version (top-level)
        """
        try:
            if isinstance(self.app, dict):
                version_value = self.app.get("version")
                if version_value:
                    return str(version_value)

            application_section = self.setting_data.get("application")
            if isinstance(application_section, dict):
                version_value = application_section.get("version")
                if version_value:
                    return str(version_value)

            top_level_version = (
                self.setting_data.get("version")
                or self.setting_data.get("app_version")
            )
            if top_level_version:
                return str(top_level_version)
        except Exception:
            return ""
        return ""

    @property
    def app_icon(self):
        """Return application icon path from settings.toml.
        
        Returns the icon path specified in app.icon, or default path if missing.
        The path is relative to the project root.
        """
        try:
            if isinstance(self.app, dict):
                icon_value = self.app.get("icon")
                if icon_value:
                    # Convert path to absolute path
                    project_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
                    return os.path.join(project_path, icon_value)
            
            # Default icon path
            project_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
            return os.path.join(project_path, "design_files", "images", "saleflex.ico")
        except Exception:
            return ""
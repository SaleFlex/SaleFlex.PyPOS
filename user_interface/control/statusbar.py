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

from PySide6 import QtGui
from PySide6.QtCore import QTimer, Slot, QDateTime
from PySide6.QtGui import QFont, QPalette, QColor, Qt
from PySide6.QtWidgets import QStatusBar, QLabel


class StatusBar(QStatusBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            """
                background:gray;
                color:black;
                font: 12pt \"Consolas\";
            """)
        date_time_timer = QTimer(self, interval=1000, timeout=self.show_date_time)
        date_time_timer.start()
        self.date_time_label = QLabel("")
        self.addPermanentWidget(self.date_time_label)
        self.show_date_time()

    @Slot()
    def show_date_time(self):
        date_time = QDateTime.currentDateTime()
        self.date_time_label.setText(
            date_time.toString('yyyy MM dd hh mm' if date_time.time().second() % 2 == 0 else 'yyyy-MM-dd hh:mm'))


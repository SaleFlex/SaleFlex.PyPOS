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


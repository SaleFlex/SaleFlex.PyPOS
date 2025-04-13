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

import time

from PySide6.QtCore import QThread, QObject


class KeyAnimationThread (QThread):

    def __init__(self, signal, parent):
        super(KeyAnimationThread, self).__init__(parent)
        self.signal = signal

    def run(self):
        for i in range(25):
            self.signal.emit(i + 1)
            time.sleep(0.01)

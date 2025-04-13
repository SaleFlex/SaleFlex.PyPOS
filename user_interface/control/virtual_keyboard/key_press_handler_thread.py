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

import threading
import time

from PySide6 import QtCore


class KeyPressHandlerThread (QtCore.QThread):

    def __init__(self, signal, key, parent):
        super(KeyPressHandlerThread, self).__init__(parent)
        self.signal = signal
        self.key = key
        self.isKeyRelease = False
        self.threadIsStarted = False
        self.lock = threading.Lock()

    def setisKeyRelease(self, flag):
        self.lock.acquire()
        self.isKeyRelease = flag
        self.lock.release()

    def checkKeyRelease(self):
        self.lock.acquire()
        val = self.isKeyRelease
        self.lock.release()
        return val

    def run(self):
        if self.key == "Backspace":
            self.setisKeyRelease(False)
            self.signal.emit()
            time.sleep(1)
            while True:
                if not self.checkKeyRelease():
                    self.signal.emit()
                    time.sleep(0.05)
                else:
                    break
        # self.threadIsStarted = False
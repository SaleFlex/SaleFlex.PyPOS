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
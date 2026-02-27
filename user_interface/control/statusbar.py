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

from core.logger import get_logger
from data_layer.auto_save import AutoSaveModel, AutoSaveDict

logger = get_logger(__name__)


class StatusBar(QStatusBar):
    def __init__(self, app=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.setStyleSheet(
            """
                background:gray;
                color:black;
                font: 12pt \"Consolas\";
            """)
        
        # Create left side label for cashier and document info
        self.info_label = QLabel("")
        self.addWidget(self.info_label)
        
        # Create right side label for date/time
        self.date_time_label = QLabel("")
        self.addPermanentWidget(self.date_time_label)
        
        # Timer for updating date/time
        self.date_time_timer = QTimer(self)
        self.date_time_timer.setInterval(1000)
        self.date_time_timer.timeout.connect(self.update_display)
        self.date_time_timer.start()

        
        # Initial update
        self.update_display()

    @Slot()
    def update_display(self):
        """Update both date/time and info labels"""
        # Update date/time
        date_time = QDateTime.currentDateTime()
        self.date_time_label.setText(
            date_time.toString('yyyy MM dd hh mm' if date_time.time().second() % 2 == 0 else 'yyyy-MM-dd hh:mm'))
        
        # Update info label (cashier, transaction, closure info)
        self.update_info_label()

    def update_info_label(self):
        """Update the left side info label with cashier, transaction, and closure information"""
        if not self.app:
            self.info_label.setText("")
            return
        
        info_parts = []
        
        # Get cashier info
        try:
            cashier_data = self.app.cashier_data
            if cashier_data:
                # Unwrap if it's an AutoSaveModel
                if isinstance(cashier_data, AutoSaveModel):
                    cashier_data = cashier_data.unwrap()
                
                cashier_name = f"{cashier_data.name} {cashier_data.last_name}".strip()
                if cashier_name:
                    info_parts.append(cashier_name)
        except Exception:
            pass
        
        # Get document/transaction info
        try:
            document_data = self.app.document_data
            
            if document_data:
                # Unwrap if it's an AutoSaveDict
                if isinstance(document_data, AutoSaveDict):
                    document_data = document_data.unwrap()
                
                head = document_data.get("head")
                
                if head:
                    # Unwrap if it's an AutoSaveModel
                    if isinstance(head, AutoSaveModel):
                        head = head.unwrap()
                    
                    # Get attributes - try both direct access and getattr
                    document_type = None
                    transaction_type = None
                    receipt_number = None
                    
                    try:
                        document_type = head.document_type if hasattr(head, 'document_type') else None
                    except:
                        pass
                    
                    try:
                        transaction_type = head.transaction_type if hasattr(head, 'transaction_type') else None
                    except:
                        pass
                    
                    try:
                        receipt_number = head.receipt_number if hasattr(head, 'receipt_number') else None
                    except:
                        pass
                    
                    if not document_type and not transaction_type and receipt_number is None:
                        logger.warning("[StatusBar] All document fields are None/empty")
                        logger.debug("[StatusBar] head type: %s, head attributes: %s", type(head), dir(head) if hasattr(head, '__dict__') else 'N/A')
                        if hasattr(head, '__dict__'):
                            logger.debug("[StatusBar] head.__dict__: %s", head.__dict__)
                    
                    transaction_info = []
                    if document_type:
                        transaction_info.append(f"Doc: {document_type}")
                    if transaction_type:
                        transaction_info.append(f"Type: {transaction_type}")
                    if receipt_number is not None:
                        transaction_info.append(f"Receipt: {receipt_number}")
                    
                    if transaction_info:
                        info_parts.append(" | ".join(transaction_info))
        except Exception as e:
            logger.exception("[StatusBar] Error getting document info: %s", e)
        
        # Get closure info
        try:
            closure = self.app.closure
            if closure:
                # Unwrap if it's an AutoSaveDict
                if isinstance(closure, AutoSaveDict):
                    closure = closure.unwrap()
                
                closure_obj = closure.get("closure")
                if closure_obj:
                    # Unwrap if it's an AutoSaveModel
                    if isinstance(closure_obj, AutoSaveModel):
                        closure_obj = closure_obj.unwrap()
                    
                    closure_number = getattr(closure_obj, 'closure_number', None)
                    if closure_number is not None:
                        info_parts.append(f"Closure: {closure_number}")
        except Exception:
            pass
        
        # Set the info label text
        info_text = " | ".join(info_parts) if info_parts else ""
        self.info_label.setText(info_text)


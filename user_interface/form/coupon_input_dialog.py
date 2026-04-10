"""
Modal dialog to enter or scan a coupon / promotion code on the SALE screen.

Copyright (c) 2025-2026 Ferhat Mousavi
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class CouponInputDialog(QDialog):
    """Alphanumeric coupon or barcode entry; Enter confirms."""

    _W = 420
    _H = 200

    def __init__(self, parent=None, initial_text: str = "") -> None:
        super().__init__(parent)
        self._result: str | None = None
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(self._W, self._H)

        layout = QVBoxLayout(self)
        title = QLabel("Coupon / promotion code")
        title.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        hint = QLabel("Type a code, paste, or scan (barcode).")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._edit = QLineEdit(self)
        self._edit.setPlaceholderText("Code or barcode")
        self._edit.setMaxLength(200)
        if initial_text:
            self._edit.setText(initial_text.strip())
        self._edit.setFont(QFont("Tahoma", 14))
        layout.addWidget(self._edit)

        row = QHBoxLayout()
        apply_btn = QPushButton("APPLY")
        apply_btn.setMinimumHeight(40)
        apply_btn.clicked.connect(self._on_apply)
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        row.addWidget(apply_btn)
        row.addWidget(cancel_btn)
        layout.addLayout(row)

        for sc in (Qt.Key_Return, Qt.Key_Enter):
            shortcut = QShortcut(QKeySequence(sc), self)
            shortcut.activated.connect(self._on_apply)

        self._center()

    def _center(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                geo.center().x() - self.width() // 2,
                geo.center().y() - self.height() // 2,
            )

    def _on_apply(self) -> None:
        text = self._edit.text().strip()
        if not text:
            return
        self._result = text
        self.accept()

    def result_code(self) -> str | None:
        if self.result() == QDialog.DialogCode.Accepted:
            return self._result
        return None

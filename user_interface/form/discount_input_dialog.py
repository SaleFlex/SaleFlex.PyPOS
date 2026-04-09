"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

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

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QGuiApplication, QFont, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QGridLayout, QWidget,
)

from user_interface.control.textbox import TextBox


class DiscountInputDialog(QDialog):
    """
    Modal dialog for entering a discount or markup value (percentage or fixed amount).

    Uses an editable TextBox with an embedded numpad for touch entry. The window
    VirtualKeyboard is intentionally not attached so focus does not open the on-screen
    QWERTY keyboard; use the dialog keys or a physical keyboard. Enter/Return triggers APPLY.
    """

    MODE_DISCOUNT_PERCENT = "DISCOUNT_PERCENT"
    MODE_DISCOUNT_AMOUNT = "DISCOUNT_AMOUNT"
    MODE_MARKUP_PERCENT = "MARKUP_PERCENT"
    MODE_MARKUP_AMOUNT = "MARKUP_AMOUNT"

    _W = 440
    _H = 520

    def __init__(
        self,
        parent=None,
        mode: str = MODE_DISCOUNT_PERCENT,
        product_name: str = "",
        max_value: float = 100.0,
        decimal_places: int = 2,
    ) -> None:
        super().__init__(parent)

        self.mode = mode
        self.product_name = product_name
        self.max_value = max_value
        self.decimal_places = decimal_places
        self._result = None

        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(self._W, self._H)

        self._build_ui()
        self._center_on_screen()

        for sc in (Qt.Key_Return, Qt.Key_Enter):
            shortcut = QShortcut(QKeySequence(sc), self)
            shortcut.activated.connect(self._on_apply)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QWidget(self)
        if self.mode == self.MODE_DISCOUNT_PERCENT:
            header.setStyleSheet("background-color: #7B1FA2;")
            title_text = "DISCOUNT BY PERCENTAGE  (%)"
        elif self.mode == self.MODE_DISCOUNT_AMOUNT:
            header.setStyleSheet("background-color: #D84315;")
            title_text = "DISCOUNT BY AMOUNT"
        elif self.mode == self.MODE_MARKUP_PERCENT:
            header.setStyleSheet("background-color: #00695C;")
            title_text = "MARKUP BY PERCENTAGE  (%)"
        else:
            header.setStyleSheet("background-color: #1565C0;")
            title_text = "MARKUP BY AMOUNT"

        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 12, 16, 12)
        title_lbl = QLabel(title_text, header)
        title_lbl.setFont(QFont("Tahoma", 14, QFont.Bold))
        title_lbl.setStyleSheet("color: #FFFFFF; background: transparent;")
        title_lbl.setAlignment(Qt.AlignCenter)
        h_lay.addWidget(title_lbl)
        outer.addWidget(header)

        info_widget = QWidget(self)
        info_widget.setStyleSheet("background-color: #37474F;")
        info_lay = QVBoxLayout(info_widget)
        info_lay.setContentsMargins(12, 8, 12, 8)
        info_lay.setSpacing(2)

        prod_lbl = QLabel(self.product_name, info_widget)
        prod_lbl.setFont(QFont("Tahoma", 11, QFont.Bold))
        prod_lbl.setStyleSheet("color: #ECEFF1; background: transparent;")
        prod_lbl.setAlignment(Qt.AlignCenter)
        prod_lbl.setWordWrap(True)
        info_lay.addWidget(prod_lbl)

        if "PERCENT" in self.mode:
            range_text = "Enter percentage: 1 % – 100 %"
        else:
            fmt = f"0.{'0' * self.decimal_places}"
            max_fmt = f"{self.max_value:.{self.decimal_places}f}"
            range_text = f"Enter amount: {fmt} – {max_fmt}"

        range_lbl = QLabel(range_text, info_widget)
        range_lbl.setFont(QFont("Tahoma", 10))
        range_lbl.setStyleSheet("color: #B0BEC5; background: transparent;")
        range_lbl.setAlignment(Qt.AlignCenter)
        info_lay.addWidget(range_lbl)
        outer.addWidget(info_widget)

        body = QWidget(self)
        body.setStyleSheet("background-color: #263238;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(20, 14, 20, 6)
        body_lay.setSpacing(10)

        self._display = TextBox(body)
        self._display.setReadOnly(False)
        self._display.setAlignment(Qt.AlignRight)
        self._display.setFont(QFont("Tahoma", 26, QFont.Bold))
        self._display.setFixedHeight(60)
        self._display.setStyleSheet("""
            QLineEdit {
                background-color: #ECEFF1;
                color: #212121;
                border: 2px solid #90A4AE;
                border-radius: 6px;
                padding: 4px 10px;
            }
        """)
        self._display.setPlaceholderText("0")
        self._display.enter_function = self._on_apply
        body_lay.addWidget(self._display)

        grid_widget = QWidget(body)
        grid = QGridLayout(grid_widget)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)

        keys = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            (".", 3, 0), ("0", 3, 1), ("⌫", 3, 2),
        ]

        for label, row, col in keys:
            btn = self._make_key_button(label, body)
            grid.addWidget(btn, row, col)

        body_lay.addWidget(grid_widget)

        act_widget = QWidget(body)
        act_lay = QHBoxLayout(act_widget)
        act_lay.setContentsMargins(0, 4, 0, 0)
        act_lay.setSpacing(10)

        clear_btn = self._make_action_button("CLEAR", "#546E7A", "#FFFFFF")
        clear_btn.clicked.connect(self._on_clear)
        act_lay.addWidget(clear_btn)

        apply_btn = self._make_action_button("APPLY", "#1B5E20", "#FFFFFF")
        apply_btn.clicked.connect(self._on_apply)
        act_lay.addWidget(apply_btn)

        cancel_btn = self._make_action_button("CANCEL", "#B71C1C", "#FFFFFF")
        cancel_btn.clicked.connect(self.reject)
        act_lay.addWidget(cancel_btn)

        body_lay.addWidget(act_widget)
        outer.addWidget(body)

    def _make_key_button(self, label: str, parent: QWidget) -> QPushButton:
        btn = QPushButton(label, parent)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setFont(QFont("Tahoma", 18, QFont.Bold))
        btn.setFixedHeight(58)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #455A64;
                color: #ECEFF1;
                border: 1px solid #607D8B;
                border-radius: 6px;
            }
            QPushButton:pressed {
                background-color: #78909C;
            }
        """)
        btn.clicked.connect(lambda checked=False, k=label: self._on_key(k))
        return btn

    def _make_action_button(self, label: str, bg: str, fg: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setFont(QFont("Tahoma", 13, QFont.Bold))
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: {bg}AA;
            }}
        """)
        return btn

    def showEvent(self, event):
        super().showEvent(event)
        self._display.setFocus()

    def _entry_text(self) -> str:
        return self._display.text().strip()

    def _on_key(self, key: str) -> None:
        t = self._display.text()
        if key == "⌫":
            self._display.setText(t[:-1])
            return
        if key == ".":
            if "." not in t:
                if not t:
                    t = "0"
                self._display.setText(t + ".")
            return

        if "." in t:
            decimals_entered = len(t.split(".")[1])
            if decimals_entered >= self.decimal_places:
                return
        self._display.setText(t + key)

    def _on_clear(self) -> None:
        self._display.clear()

    def _on_apply(self) -> None:
        text = self._entry_text()
        if not text or text == ".":
            self._show_error("Please enter a value.")
            return

        try:
            value = float(text)
        except ValueError:
            self._show_error("Invalid number.")
            return

        if "PERCENT" in self.mode:
            if value < 1.0 or value > 100.0:
                self._show_error("Percentage must be between 1 % and 100 %.")
                return
        else:
            min_val = 10 ** (-self.decimal_places)
            if value < min_val or value > self.max_value:
                self._show_error(
                    f"Amount must be between "
                    f"{min_val:.{self.decimal_places}f} "
                    f"and {self.max_value:.{self.decimal_places}f}."
                )
                return

        self._result = value
        self.accept()

    def _show_error(self, message: str) -> None:
        from user_interface.form.message_form import MessageForm
        MessageForm.show_error(self, message, "")

    def get_result(self) -> float | None:
        return self._result

    def _center_on_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo: QRect = screen.geometry()
        x = geo.x() + (geo.width() - self._W) // 2
        y = geo.y() + (geo.height() - self._H) // 2
        self.move(x, y)

    @staticmethod
    def show_percent(parent, product_name: str,
                     product_total: float) -> float | None:
        dlg = DiscountInputDialog(
            parent=parent,
            mode=DiscountInputDialog.MODE_DISCOUNT_PERCENT,
            product_name=product_name,
            max_value=100.0,
            decimal_places=2,
        )
        if dlg.exec() == QDialog.Accepted:
            return dlg.get_result()
        return None

    @staticmethod
    def show_amount(parent, product_name: str,
                    product_total: float,
                    decimal_places: int = 2) -> float | None:
        dlg = DiscountInputDialog(
            parent=parent,
            mode=DiscountInputDialog.MODE_DISCOUNT_AMOUNT,
            product_name=product_name,
            max_value=product_total,
            decimal_places=decimal_places,
        )
        if dlg.exec() == QDialog.Accepted:
            return dlg.get_result()
        return None

    @staticmethod
    def show_markup_percent(parent, product_name: str,
                            product_total: float) -> float | None:
        dlg = DiscountInputDialog(
            parent=parent,
            mode=DiscountInputDialog.MODE_MARKUP_PERCENT,
            product_name=product_name,
            max_value=100.0,
            decimal_places=2,
        )
        if dlg.exec() == QDialog.Accepted:
            return dlg.get_result()
        return None

    @staticmethod
    def show_markup_amount(parent, product_name: str,
                           product_total: float,
                           decimal_places: int = 2) -> float | None:
        dlg = DiscountInputDialog(
            parent=parent,
            mode=DiscountInputDialog.MODE_MARKUP_AMOUNT,
            product_name=product_name,
            max_value=product_total,
            decimal_places=decimal_places,
        )
        if dlg.exec() == QDialog.Accepted:
            return dlg.get_result()
        return None

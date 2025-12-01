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

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class NumPadButton(QtWidgets.QPushButton):
    """ KeyButton class to be used by NumPad class
    """
    key_button_clicked_signal = QtCore.Signal(str)

    def __init__(self, key, parent=None, button_width=80, button_height=80, 
                 number_font_size=24, action_font_size=16, enter_font_size=18):
        """ KeyButton class constructor

        Parameters
        ----------
        key : str
            key of the button
        parent : QWidget, optional
            Parent widget (the default is None)
        button_width : int, optional
            Width of the button (default is 80)
        button_height : int, optional
            Height of the button (default is 80)
        number_font_size : int, optional
            Font size for number buttons (default is 24)
        action_font_size : int, optional
            Font size for action buttons (default is 16)
        enter_font_size : int, optional
            Font size for Enter button (default is 18)
        """
        super(NumPadButton, self).__init__(parent)
        self._key = key
        self._button_width = button_width
        self._button_height = button_height
        self._number_font_size = number_font_size
        self._action_font_size = action_font_size
        self._enter_font_size = enter_font_size

        # Visual configuration placeholders - updated by NumPad
        self._base_bg_color = QColor("#3c3c3c")
        self._hover_bg_color = QColor("#3f3f3f")
        self._pressed_bg_color = QColor("#2b2b2b")
        self._text_color = QColor("#ffffff")
        self._text_disabled_color = QColor("#8c8c8c")
        self._border_color = QColor("#000000")
        self._border_radius = 6
        self._border_width = 1
        self._min_width = button_width
        self._max_width = button_width
        self._min_height = button_height
        self._max_height = button_height
        self._font_family = "Noto Sans CJK JP"
        self._font_size = number_font_size
        self._font_weight = "bold"
        self._current_bg_color = QColor(self._base_bg_color)
        self._disabled_bg_color = QColor("#2b2b2b")

        # Animation state
        self._hover_progress = 0.0
        self._press_progress = 0.0

        self.set_key(key)
        self.clicked.connect(self.emit_key)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        self._setup_shadow_effect()
        self._setup_animations()

    def set_key(self, key):
        """ KeyButton class method to set the key and text of button

        Parameters
        ----------
        key : str
            key of the button
        """
        self._key = key
        self.setText(key)

    def apply_visual_profile(self, *, base_bg, hover_bg, pressed_bg, text_color,
                             border_color, border_radius, border_width,
                             font_family, font_size, font_weight,
                             min_width, max_width, min_height, max_height,
                             disabled_bg=None, disabled_text=None):
        """Configure the visual profile for the button and refresh the style."""
        self._base_bg_color = QColor(base_bg)
        self._hover_bg_color = QColor(hover_bg)
        self._pressed_bg_color = QColor(pressed_bg)
        self._text_color = QColor(text_color)
        self._border_color = QColor(border_color)
        self._border_radius = border_radius
        self._border_width = border_width
        self._font_family = font_family
        self._font_size = font_size
        self._font_weight = font_weight
        self._min_width = min_width
        self._max_width = max_width
        self._min_height = min_height
        self._max_height = max_height

        self._button_width = min_width if min_width is not None else self._button_width
        self._button_height = min_height if min_height is not None else self._button_height

        self._disabled_bg_color = QColor(disabled_bg) if disabled_bg else QColor(self._base_bg_color).darker(140)
        if disabled_text:
            self._text_disabled_color = QColor(disabled_text)
        else:
            self._text_disabled_color = QColor(self._text_color).darker(140)

        self._current_bg_color = QColor(self._base_bg_color)

        self._apply_stylesheet()
        self._update_shadow_state()

    def emit_key(self):
        """ KeyButton class method to return key as a qt signal
        """
        self.key_button_clicked_signal.emit(str(self._key))

    def sizeHint(self):
        """ KeyButton class method to return size

        Returns
        -------
        QSize
            Size of the created button
        """
        return QtCore.QSize(self._button_width, self._button_height)

    def key_disabled(self, flag):
        self.setDisabled(flag)

    def enterEvent(self, event):
        self._animate_hover(1.0)
        super(NumPadButton, self).enterEvent(event)

    def leaveEvent(self, event):
        self._animate_hover(0.0)
        super(NumPadButton, self).leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.rect().contains(event.pos()):
            # Release happened outside of the button - reset the press animation
            self._animate_press(0.0)
        super(NumPadButton, self).mouseReleaseEvent(event)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.EnabledChange and not self.isEnabled():
            self._hover_anim.stop()
            self._press_anim.stop()
            self._hover_progress = 0.0
            self._press_progress = 0.0
            self._update_visual_state()
        super(NumPadButton, self).changeEvent(event)

    def _setup_shadow_effect(self):
        """Create a drop shadow effect that we can animate."""
        self._shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self)
        self._shadow_effect.setBlurRadius(12)
        self._shadow_effect.setOffset(0, 3)
        self._shadow_effect.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(self._shadow_effect)

        self._shadow_levels = {
            "base": {"blur": 12, "offset": 3},
            "hover": {"blur": 22, "offset": 6},
            "pressed": {"blur": 6, "offset": 1},
        }

    def _setup_animations(self):
        """Prepare hover and press animations."""
        self._hover_anim = QtCore.QVariantAnimation(self)
        self._hover_anim.setDuration(180)
        self._hover_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._hover_anim.valueChanged.connect(self._set_hover_progress)

        self._press_anim = QtCore.QVariantAnimation(self)
        self._press_anim.setDuration(110)
        self._press_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._press_anim.valueChanged.connect(self._set_press_progress)

        self.pressed.connect(self._handle_pressed_state)
        self.released.connect(self._handle_released_state)

    def _handle_pressed_state(self):
        self._animate_press(1.0)

    def _handle_released_state(self):
        self._animate_press(0.0)

    def _set_hover_progress(self, value):
        self._hover_progress = float(value)
        self._update_visual_state()

    def _set_press_progress(self, value):
        self._press_progress = float(value)
        self._update_visual_state()

    def _animate_hover(self, target):
        if not self.isEnabled():
            target = 0.0
        if abs(self._hover_progress - target) < 0.01:
            return
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(target)
        self._hover_anim.start()

    def _animate_press(self, target):
        if abs(self._press_progress - target) < 0.01:
            return
        self._press_anim.stop()
        self._press_anim.setStartValue(self._press_progress)
        self._press_anim.setEndValue(target)
        self._press_anim.start()

    def _update_visual_state(self):
        if not self._base_bg_color:
            return

        bg_color = QColor(self._base_bg_color)
        if self._hover_bg_color:
            bg_color = self._blend_colors(bg_color, self._hover_bg_color, self._hover_progress)
        if self._pressed_bg_color:
            bg_color = self._blend_colors(bg_color, self._pressed_bg_color, self._press_progress)

        self._current_bg_color = QColor(bg_color)
        self._apply_stylesheet()
        self._update_shadow_state()

    def _apply_stylesheet(self):
        width_section = ""
        height_section = ""

        if self._min_width is not None:
            width_section += f"min-width: {self._min_width}px;\n"
        if self._max_width is not None:
            width_section += f"max-width: {self._max_width}px;\n"
        if self._min_height is not None:
            height_section += f"min-height: {self._min_height}px;\n"
        if self._max_height is not None:
            height_section += f"max-height: {self._max_height}px;\n"

        style = f"""
            QPushButton {{
                {width_section if width_section else ''}
                {height_section if height_section else ''}
                font-size: {self._font_size}px;
                font-weight: {self._font_weight};
                font-family: {self._font_family};
                border: {self._border_width}px solid {self._border_color.name()};
                border-radius: {self._border_radius}px;
                background-color: {self._current_bg_color.name()};
                color: {self._text_color.name()};
            }}
            QPushButton:disabled {{
                background-color: {self._disabled_bg_color.name()};
                color: {self._text_disabled_color.name()};
            }}
        """
        self.setStyleSheet(style)

    def _update_shadow_state(self):
        if not hasattr(self, "_shadow_effect"):
            return

        base = self._shadow_levels["base"]
        hover = self._shadow_levels["hover"]
        pressed = self._shadow_levels["pressed"]

        blur = self._lerp(base["blur"], hover["blur"], self._hover_progress)
        offset = self._lerp(base["offset"], hover["offset"], self._hover_progress)

        blur = self._lerp(blur, pressed["blur"], self._press_progress)
        offset = self._lerp(offset, pressed["offset"], self._press_progress)

        self._shadow_effect.setBlurRadius(blur)
        self._shadow_effect.setYOffset(offset)

    @staticmethod
    def _blend_colors(source, target, progress):
        progress = max(0.0, min(1.0, progress))
        result = QColor(source)
        result.setRed(int(source.red() + (target.red() - source.red()) * progress))
        result.setGreen(int(source.green() + (target.green() - source.green()) * progress))
        result.setBlue(int(source.blue() + (target.blue() - source.blue()) * progress))
        return result

    @staticmethod
    def _lerp(start, end, progress):
        return start + (end - start) * progress

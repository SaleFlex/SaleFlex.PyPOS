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

from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtCore import Qt


class Button(QPushButton):
    def __init__(self, *args, font_name="Verdana", **kwargs):
        super().__init__(*args, **kwargs)
        self._base_font_size = 20
        self._font_name = font_name
        self.setFont(QFont(self._font_name, self._base_font_size))
        # Enable word wrap for multi-line text via CSS
        self._word_wrap_enabled = True
        
    def setText(self, text):
        """Override setText to auto-adjust font size and wrap text"""
        # Store original text
        self._original_text = text
        # Set text without triggering adjustment (to avoid recursion)
        QPushButton.setText(self, text)
        # Adjust font size after text is set
        self._adjust_font_size()
    
    def _adjust_font_size(self):
        """Automatically adjust font size to fit button dimensions"""
        if not hasattr(self, '_original_text') or not self._original_text:
            return
        
        # Get button dimensions (accounting for padding)
        button_width = self.width() - 10  # Subtract padding
        button_height = self.height() - 10  # Subtract padding
        
        if button_width <= 0 or button_height <= 0:
            return
        
        # Start with base font size
        font_size = self._base_font_size
        font = QFont(self._font_name, font_size)
        font_metrics = QFontMetrics(font)
        
        # Work with original text
        original_text = self._original_text
        
        # Check if text fits in one line
        text_width = font_metrics.horizontalAdvance(original_text)
        text_height = font_metrics.height()
        
        # Determine if we should split into two lines
        words = original_text.split()
        final_text = original_text
        use_two_lines = False
        
        # If text is too wide and has multiple words, try to split into two lines
        if len(words) > 1 and text_width > button_width:
            # Try splitting into two lines
            mid_point = len(words) // 2
            line1 = ' '.join(words[:mid_point])
            line2 = ' '.join(words[mid_point:])
            
            line1_width = font_metrics.horizontalAdvance(line1)
            line2_width = font_metrics.horizontalAdvance(line2)
            max_line_width = max(line1_width, line2_width)
            
            # If two lines fit better, use them
            if max_line_width < text_width and (text_height * 2) <= button_height:
                final_text = f"{line1}\n{line2}"
                use_two_lines = True
                text_width = max_line_width
                text_height = text_height * 2
        
        # Reduce font size if text doesn't fit
        min_font_size = 8  # Minimum readable font size
        while (text_width > button_width or text_height > button_height) and font_size > min_font_size:
            font_size -= 1
            font = QFont(self._font_name, font_size)
            font_metrics = QFontMetrics(font)
            
            # Recalculate with new font size
            if use_two_lines:
                lines = final_text.split('\n')
                text_width = max([font_metrics.horizontalAdvance(line) for line in lines])
                text_height = font_metrics.height() * len(lines)
            else:
                text_width = font_metrics.horizontalAdvance(original_text)
                text_height = font_metrics.height()
        
        # Apply the adjusted font and set final text
        font = QFont(self._font_name, font_size)
        self.setFont(font)
        # Set text directly to avoid recursion
        QPushButton.setText(self, final_text)
        
    def resizeEvent(self, event):
        """Override resizeEvent to adjust font when button is resized"""
        super().resizeEvent(event)
        self._adjust_font_size()
        
    def set_color(self, background_color, foreground_color):
        # 3D appearance with gradient and border effect
        word_wrap_style = "word-wrap: break-word;" if self._word_wrap_enabled else ""
        style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #{background_color:06X},
                    stop:0.5 #{self._darken_color(background_color, 0.85):06X},
                    stop:1 #{self._darken_color(background_color, 0.7):06X});
                color: #{foreground_color:06X};
                border: 2px solid #{self._darken_color(background_color, 0.5):06X};
                border-radius: 6px;
                padding: 5px;
                {word_wrap_style}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #{self._lighten_color(background_color, 1.15):06X},
                    stop:0.5 #{background_color:06X},
                    stop:1 #{self._darken_color(background_color, 0.75):06X});
                border: 2px solid #{self._darken_color(background_color, 0.4):06X};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #{self._darken_color(background_color, 0.6):06X},
                    stop:0.5 #{self._darken_color(background_color, 0.75):06X},
                    stop:1 #{self._darken_color(background_color, 0.85):06X});
                border: 2px solid #{self._darken_color(background_color, 0.3):06X};
                padding-top: 7px;
                padding-left: 7px;
            }}
            QPushButton:disabled {{
                background: #CCCCCC;
                color: #888888;
                border: 2px solid #999999;
            }}
        """
        self.setStyleSheet(style)

    def _darken_color(self, color, factor):
        """Darken the color by factor"""
        r = int(((color >> 16) & 0xFF) * factor)
        g = int(((color >> 8) & 0xFF) * factor)
        b = int((color & 0xFF) * factor)
        return (r << 16) | (g << 8) | b
    
    def _lighten_color(self, color, factor):
        """Lighten the color by factor"""
        r = min(255, int(((color >> 16) & 0xFF) * factor))
        g = min(255, int(((color >> 8) & 0xFF) * factor))
        b = min(255, int((color & 0xFF) * factor))
        return (r << 16) | (g << 8) | b

    def set_event(self, function):
        self.click()


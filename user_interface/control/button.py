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

from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont, QFontMetrics


class Button(QPushButton):
    def __init__(self, *args, font_name="Verdana", **kwargs):
        super().__init__(*args, **kwargs)
        self._base_font_size = 20
        self._font_name = font_name
        self.setFont(QFont(self._font_name, self._base_font_size))
        # Text wrapping is handled programmatically in _adjust_font_size()
        
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
        # Note: word-wrap is not supported in Qt CSS, text wrapping is handled programmatically
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


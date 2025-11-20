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

from data_layer.engine import Engine
from data_layer.model.definition import PosVirtualKeyboard


class KeyboardSettingsLoader:
    """Helper class to load virtual keyboard settings from database"""
    
    _cached_settings = None
    _engine = None
    
    @classmethod
    def initialize(cls, engine: Engine):
        """Initialize the settings loader with database engine
        
        Parameters
        ----------
        engine : Engine
            Database engine instance
        """
        cls._engine = engine
        cls._cached_settings = None
    
    @classmethod
    def get_active_settings(cls):
        """Get active virtual keyboard settings from database
        
        Returns
        -------
        PosVirtualKeyboard or None
            Active keyboard settings or None if not found or disabled
        """
        # Return cached settings if available
        if cls._cached_settings is not None:
            return cls._cached_settings
        
        # If engine not initialized, return default settings
        if cls._engine is None:
            return cls._get_default_settings()
        
        try:
            with cls._engine.get_session() as session:
                # Get active keyboard settings
                settings = session.query(PosVirtualKeyboard).filter_by(
                    is_active=True,
                    is_deleted=False
                ).first()
                
                if settings:
                    # Cache the settings
                    cls._cached_settings = settings
                    return settings
                else:
                    # No active settings found, return default
                    return cls._get_default_settings()
        except Exception as e:
            print(f"⚠ Error loading keyboard settings from database: {e}")
            return cls._get_default_settings()
    
    @classmethod
    def is_keyboard_enabled(cls):
        """Check if virtual keyboard is enabled
        
        Returns
        -------
        bool
            True if keyboard is active, False otherwise
        """
        settings = cls.get_active_settings()
        return settings is not None and settings.is_active
    
    @classmethod
    def reload_settings(cls):
        """Reload settings from database (clear cache)"""
        cls._cached_settings = None
        return cls.get_active_settings()
    
    @classmethod
    def _get_default_settings(cls):
        """Get default keyboard settings (fallback)
        
        Returns
        -------
        PosVirtualKeyboard
            Default keyboard settings
        """
        return PosVirtualKeyboard(
            name="DEFAULT_FALLBACK",
            is_active=True,
            keyboard_width=970,
            keyboard_height=315,
            x_position=0,
            y_position=0,
            font_family="Noto Sans CJK JP",
            font_size=20,
            button_width=80,
            button_height=40,
            button_min_width=80,
            button_max_width=80,
            button_min_height=40,
            button_max_height=40,
            button_background_color="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde)",
            button_pressed_color="rgb(29, 150, 255)",
            button_border_color="#8f8f91",
            button_border_width=3,
            button_border_radius=8,
            space_button_min_width=450,
            space_button_max_width=550,
            special_button_min_width=100,
            special_button_max_width=200,
            control_button_width=120,
            control_button_active_color="rgb(29, 150, 255)",
            button_text_color=None,
            button_text_color_pressed=None
        )


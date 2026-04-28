"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
AutoSaveModel - Wrapper for model instances with automatic database save.

This module provides a wrapper class that automatically saves model instances
to the database whenever their attributes are modified.
"""

from core.logger import get_logger

logger = get_logger(__name__)


class AutoSaveModel:
    """
    Wrapper for model instances that automatically saves to database when attributes change.
    
    This wrapper intercepts attribute assignments and triggers database save.
    """
    
    def __init__(self, model_instance, save_callback=None):
        """
        Args:
            model_instance: The actual model instance to wrap
            save_callback: Function(model_instance) -> bool to save to database
        """
        self._model = model_instance
        self._save_callback = save_callback
        self._skip_autosave = False
    
    def __getattr__(self, name):
        """Delegate attribute access to wrapped model"""
        return getattr(self._model, name)
    
    def __setattr__(self, name, value):
        """Intercept attribute assignment and save to database"""
        # Handle internal attributes
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        # Set attribute on wrapped model
        setattr(self._model, name, value)
        
        # Auto-save if callback provided and not skipping
        if not self._skip_autosave and self._save_callback:
            try:
                self._save_callback(self._model)
            except Exception as e:
                logger.exception("Error auto-saving model after attribute change: %s", e)
    
    def __getitem__(self, key):
        """Support dictionary-like access if model supports it"""
        return self._model[key]
    
    def __setitem__(self, key, value):
        """Support dictionary-like assignment if model supports it"""
        self._model[key] = value
        if not self._skip_autosave and self._save_callback:
            try:
                self._save_callback(self._model)
            except Exception as e:
                logger.exception("Error auto-saving model after item change: %s", e)
    
    def unwrap(self):
        """Return the unwrapped model instance"""
        return self._model
    
    def __repr__(self):
        return f"AutoSaveModel({repr(self._model)})"


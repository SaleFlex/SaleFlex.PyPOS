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


"""
AutoSaveModel - Wrapper for model instances with automatic database save.

This module provides a wrapper class that automatically saves model instances
to the database whenever their attributes are modified.
"""


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
                print(f"[DEBUG] Error auto-saving model after attribute change: {e}")
                import traceback
                traceback.print_exc()
    
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
                print(f"[DEBUG] Error auto-saving model after item change: {e}")
    
    def unwrap(self):
        """Return the unwrapped model instance"""
        return self._model
    
    def __repr__(self):
        return f"AutoSaveModel({repr(self._model)})"


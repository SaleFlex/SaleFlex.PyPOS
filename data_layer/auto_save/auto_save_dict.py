"""
AutoSaveDict - Dictionary wrapper with automatic database save for nested models.

This module provides a dictionary wrapper that automatically wraps model instances
with AutoSaveModel and triggers database saves when nested models are modified.
"""

from .auto_save_model import AutoSaveModel


class AutoSaveDict(dict):
    """
    Dictionary that automatically saves nested models to database when they are modified.
    
    When a model instance in the dictionary is modified, this wrapper automatically
    triggers a save operation.
    """
    
    def __init__(self, *args, save_callback=None, **kwargs):
        """
        Args:
            *args: Positional arguments for dict initialization
            save_callback: Function(dict_instance) -> bool to save entire dict to database
            **kwargs: Keyword arguments for dict initialization
        """
        super().__init__(*args, **kwargs)
        self._save_callback = save_callback
        self._skip_autosave = False
    
    def __setitem__(self, key, value):
        """Intercept item assignment and wrap model instances"""
        # Wrap model instances with AutoSaveModel
        if value is not None:
            if hasattr(value, '__dict__') and hasattr(value, 'save'):
                # It's a model instance, wrap it
                wrapped_value = AutoSaveModel(value, save_callback=self._save_nested_model)
                super().__setitem__(key, wrapped_value)
                return
            elif isinstance(value, list):
                # Wrap list items that are models
                wrapped_list = []
                for item in value:
                    if item is not None and hasattr(item, '__dict__') and hasattr(item, 'save'):
                        wrapped_list.append(AutoSaveModel(item, save_callback=self._save_nested_model))
                    else:
                        wrapped_list.append(item)
                super().__setitem__(key, wrapped_list)
                return
        
        super().__setitem__(key, value)
    
    def _save_nested_model(self, model_instance):
        """Save callback for nested models - saves the entire dictionary"""
        if not self._skip_autosave and self._save_callback:
            return self._save_callback(self)
        return True
    
    def update(self, *args, **kwargs):
        """Override update to wrap models"""
        for key, value in dict(*args, **kwargs).items():
            self[key] = value
    
    def setdefault(self, key, default=None):
        """Override setdefault to wrap models"""
        if key not in self:
            self[key] = default
        return self[key]
    
    def unwrap(self):
        """Return unwrapped dictionary with original model instances"""
        unwrapped = {}
        for key, value in self.items():
            if isinstance(value, AutoSaveModel):
                unwrapped[key] = value.unwrap()
            elif isinstance(value, list):
                unwrapped[key] = [
                    item.unwrap() if isinstance(item, AutoSaveModel) else item
                    for item in value
                ]
            else:
                unwrapped[key] = value
        return unwrapped


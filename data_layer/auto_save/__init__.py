"""
Auto-save package for automatic database persistence.

This package provides wrappers and descriptors that automatically save
model instances and dictionaries to the database when they are modified.

Modules:
    auto_save_model: Wrapper for model instances with automatic save
    auto_save_dict: Dictionary wrapper with automatic save for nested models
    auto_save_descriptor: Descriptor for automatic save on attribute assignment
"""

from .auto_save_model import AutoSaveModel
from .auto_save_dict import AutoSaveDict
from .auto_save_descriptor import AutoSaveDescriptor

__all__ = ['AutoSaveModel', 'AutoSaveDict', 'AutoSaveDescriptor']


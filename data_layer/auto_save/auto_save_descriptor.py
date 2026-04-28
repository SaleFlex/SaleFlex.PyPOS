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
AutoSaveDescriptor - Descriptor for automatic database save on attribute assignment.

This module provides a descriptor that automatically saves data to the database
when an attribute is set, with support for wrapping dictionaries and models.
"""

from .auto_save_dict import AutoSaveDict
from core.logger import get_logger

logger = get_logger(__name__)


class AutoSaveDescriptor:
    """
    Descriptor that automatically saves data to database when attribute is set.
    
    During __init__, data can be set directly to private attribute (_attr_name)
    to skip database save. Normal attribute access uses property which triggers
    save on write.
    
    Usage:
        class MyClass:
            attr = AutoSaveDescriptor('_attr', save_callback=lambda obj, val: val.save())
            
            def __init__(self):
                self._attr = None  # Direct assignment, no save
                
            def some_method(self):
                self.attr = new_value  # Triggers save_callback
    """
    
    def __init__(self, private_attr_name, save_callback=None):
        """
        Args:
            private_attr_name: Name of the private attribute to store value
            save_callback: Function(obj, value) -> bool to save value to database
                          If None, no save operation is performed
        """
        self.private_attr_name = private_attr_name
        self.save_callback = save_callback
    
    def __get__(self, obj, objtype=None):
        """Return the value from private attribute"""
        if obj is None:
            return self
        return getattr(obj, self.private_attr_name, None)
    
    def __set__(self, obj, value):
        """
        Set value: wrap dictionaries/models if needed, save to database (if callback provided), 
        then update attribute. Skip save if value is None or if obj._skip_autosave is True.
        """
        if obj is None:
            return
        
        # Skip save during initialization or if explicitly disabled
        skip_save = getattr(obj, '_skip_autosave', False)
        
        # Wrap dictionaries with AutoSaveDict if they need auto-save
        wrapped_value = value
        if value is not None and not skip_save:
            # Determine which attributes should use AutoSaveDict
            dict_attributes = ['document_data', 'closure']
            if self.private_attr_name[1:] in dict_attributes:  # Remove leading underscore
                if isinstance(value, dict) and not isinstance(value, AutoSaveDict):
                    # Wrap dictionary with AutoSaveDict
                    wrapped_value = AutoSaveDict(
                        value, 
                        save_callback=lambda d: self.save_callback(obj, d) if self.save_callback else True
                    )
        
        # Save to database before updating attribute (unless skipping)
        if not skip_save and wrapped_value is not None and self.save_callback:
            try:
                success = self.save_callback(obj, wrapped_value)
                if not success:
                    logger.warning("Save callback returned False for %s", self.private_attr_name)
            except Exception as e:
                logger.exception("Error in save callback for %s: %s", self.private_attr_name, e)
                # Continue with setting value even if save failed
        
        # Update the private attribute
        setattr(obj, self.private_attr_name, wrapped_value)


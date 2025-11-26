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
AutoSaveDescriptor - Descriptor for automatic database save on attribute assignment.

This module provides a descriptor that automatically saves data to the database
when an attribute is set, with support for wrapping dictionaries and models.
"""

from .auto_save_dict import AutoSaveDict


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
                    print(f"[DEBUG] Warning: Save callback returned False for {self.private_attr_name}")
            except Exception as e:
                print(f"[DEBUG] Error in save callback for {self.private_attr_name}: {e}")
                import traceback
                traceback.print_exc()
                # Continue with setting value even if save failed
        
        # Update the private attribute
        setattr(obj, self.private_attr_name, wrapped_value)


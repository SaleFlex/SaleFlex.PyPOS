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

from user_interface.window import BaseWindow
from user_interface.window.dynamic_dialog import DynamicDialog
from user_interface.render.dynamic_renderer import DynamicFormRenderer
from data_layer.model import Form
from data_layer.enums import FormName


class Interface:
    """
    User Interface Manager for SaleFlex POS.
    
    Manages form rendering using database-driven dynamic forms.
    Supports both main window and modal dialog rendering.
    """
    
    def __init__(self, app):
        """
        Initialize the interface manager.
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.window = BaseWindow(app=self.app)
        self.active_dialogs = []  # Track modal dialogs

    def draw(self, form_id=None, form_name=None, skip_history_update=False):
        """
        Draw a form in the main window by form_id or form_name.
        
        Updates CurrentStatus with the current form information.
        
        Args:
            form_id (UUID): The ID of the form to draw
            form_name (str): The name of the form to draw
            skip_history_update (bool): If True, don't update form history (used for back navigation)
        """
        renderer = DynamicFormRenderer(form_id=form_id, form_name=form_name)
        
        # Update CurrentStatus with form information
        if renderer.form:
            # Set current_form_id
            self.app.current_form_id = renderer.form.id
            
            # Set current_form_type based on form name
            try:
                form_name_enum = FormName[renderer.form.name.upper()]
                
                # Only update if it's different from current, or if skip_history_update is False
                if skip_history_update:
                    # Directly set without going through setter to avoid history update
                    self.app._CurrentStatus__current_form_type = form_name_enum
                else:
                    # Use setter which will update history
                    if self.app.current_form_type != form_name_enum:
                        self.app.current_form_type = form_name_enum
            except (KeyError, AttributeError):
                # If form name doesn't match enum, try to keep current or set to NONE
                pass
        
        self.window.draw_window(renderer.settings, renderer.toolbar_settings, renderer.design)
        self.window.show()
        self.window.focus_text_box()

    def redraw(self, form_id=None, form_name=None, skip_history_update=False):
        """
        Redraw the main window with a new form.
        
        Updates CurrentStatus with the current form information.
        
        Args:
            form_id (UUID): The ID of the form to draw
            form_name (str): The name of the form to draw
            skip_history_update (bool): If True, don't update form history (used for back navigation)
        """
        self.window.clear()
        self.draw(form_id=form_id, form_name=form_name, skip_history_update=skip_history_update)
    
    def show_modal(self, form_id=None, form_name=None):
        """
        Show a form as a modal dialog.
        
        Args:
            form_id (UUID): The ID of the form to display
            form_name (str): The name of the form to display
            
        Returns:
            int: Dialog result code (QDialog.Accepted or QDialog.Rejected)
        """
        renderer = DynamicFormRenderer(form_id=form_id, form_name=form_name)
        
        # Create and configure dialog
        dialog = DynamicDialog(self.app, parent=self.window)
        dialog.draw_window(renderer.settings, renderer.toolbar_settings, renderer.design)
        dialog.focus_text_box()
        
        # Track active dialog
        self.active_dialogs.append(dialog)
        
        # Show modal and wait for result
        result = dialog.exec()
        
        # Cleanup
        dialog.clear()
        if dialog in self.active_dialogs:
            self.active_dialogs.remove(dialog)
        dialog.deleteLater()
        
        return result

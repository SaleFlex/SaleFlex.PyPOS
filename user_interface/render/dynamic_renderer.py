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

from data_layer.model import Form, FormControl
from data_layer.enums import FormName


class DynamicFormRenderer:
    """
    Renders forms dynamically from database definitions.
    
    This class replaces the TOML-based Interpreter by loading form and control
    definitions from the database and converting them to a format compatible
    with BaseWindow.draw_window().
    """
    
    def __init__(self, form_id=None, form_name=None):
        """
        Initialize the renderer with either form_id or form_name.
        
        Args:
            form_id (UUID): The UUID of the form to render
            form_name (str): The name of the form to render
        """
        self.form = None
        self.controls = []
        
        # Load form from database
        if form_id:
            self.form = Form.get_by_id(form_id)
        elif form_name:
            forms = Form.filter_by(name=form_name, is_deleted=False)
            if forms and len(forms) > 0:
                self.form = forms[0]
        
        # Load form controls if form was found
        if self.form:
            self.controls = FormControl.filter_by(
                fk_form_id=self.form.id, 
                is_deleted=False,
                is_visible=True
            )
    
    @property
    def settings(self):
        """
        Convert form database model to settings dict for BaseWindow.
        
        Returns:
            dict: Settings dictionary with form properties
        """
        if not self.form:
            return self._get_default_settings()
        
        # Convert hex color string to integer if needed
        def parse_color(color_str, default=0xFFFFFF):
            if not color_str:
                return default
            try:
                if isinstance(color_str, str):
                    if color_str.startswith('0x'):
                        return int(color_str, 16)
                    elif color_str.startswith('#'):
                        return int(color_str[1:], 16)
                    else:
                        return int(color_str, 16)
                return int(color_str)
            except (ValueError, TypeError):
                return default
        
        return {
            'name': self.form.caption or self.form.name or 'SaleFlex',
            'functionality': self.form.function or 'NONE',
            'login_required': self.form.need_login or False,
            'toolbar': self.form.show_in_taskbar or False,
            'statusbar': self.form.show_status_bar or False,
            'background_color': parse_color(self.form.back_color, 0xFFFFFF),
            'foreground_color': parse_color(self.form.fore_color, 0x000000),
            'width': self.form.width or 1024,
            'height': self.form.height or 768
        }
    
    @property
    def toolbar_settings(self):
        """
        Generate toolbar settings from form controls.
        
        Returns:
            dict: Toolbar configuration or None if no toolbar
        """
        if not self.form or not self.form.show_in_taskbar:
            return None
        
        # Look for toolbar control
        toolbar_control = None
        for control in self.controls:
            if control.type.lower() == 'toolbar':
                toolbar_control = control
                break
        
        if not toolbar_control:
            return None
        
        # Basic toolbar settings
        toolbar_settings = {
            'button': {}
        }
        
        # Find back button if exists
        for control in self.controls:
            if control.fk_parent_id == toolbar_control.id:
                if 'back' in control.name.lower():
                    toolbar_settings['button']['back'] = {
                        'caption': control.caption1 or 'Back',
                        'image': control.image or ''
                    }
        
        return toolbar_settings
    
    @property
    def design(self):
        """
        Convert form controls to design list for BaseWindow.
        
        Returns:
            list: List of control design dictionaries
        """
        if not self.form:
            return []
        
        design_list = []
        
        for control in self.controls:
            # Skip parent controls (like toolbar) - their children will be processed
            if control.type.lower() in ['toolbar', 'statusbar']:
                continue
            
            # Skip controls that belong to toolbar/statusbar
            if control.fk_parent_id:
                parent = self._find_control_by_id(control.fk_parent_id)
                if parent and parent.type.lower() in ['toolbar', 'statusbar']:
                    continue
            
            design_dict = self._convert_control_to_design(control)
            if design_dict:
                design_list.append(design_dict)
        
        return design_list
    
    def _convert_control_to_design(self, control):
        """
        Convert a FormControl model to design dictionary.
        
        Args:
            control (FormControl): The control to convert
            
        Returns:
            dict: Design dictionary for the control
        """
        def parse_color(color_str, default=0xFFFFFF):
            if not color_str:
                return default
            try:
                if isinstance(color_str, str):
                    if color_str.startswith('0x'):
                        return int(color_str, 16)
                    elif color_str.startswith('#'):
                        return int(color_str[1:], 16)
                    else:
                        return int(color_str, 16)
                return int(color_str)
            except (ValueError, TypeError):
                return default
        
        # Base design dictionary
        design = {
            'type': control.type.lower(),
            'name': control.name,
            'caption': control.caption1 or '',
            'location_x': control.location_x or 0,
            'location_y': control.location_y or 0,
            'width': control.width or 0,
            'height': control.height or 0,
            'background_color': parse_color(control.back_color, 0xFFFFFF),
            'foreground_color': parse_color(control.fore_color, 0x000000),
        }
        
        # Add control-specific properties
        if control.type.lower() == 'textbox':
            design.update({
                'field_name': control.name,
                'place_holder': control.caption1 or '',
                'input_type': control.input_type.lower() if control.input_type else 'alphanumeric',
                'alignment': control.text_alignment.lower() if control.text_alignment else 'left',
                'font_size': int(control.font_size) if control.font_size else 12,
                'use_keyboard': self.form.use_virtual_keyboard if self.form else False
            })
        
        elif control.type.lower() == 'button':
            # Check if button has form navigation
            if control.fk_target_form_id:
                design['function'] = f"NAVIGATE_TO_FORM:{control.fk_target_form_id}:{control.form_transition_mode or 'REPLACE'}"
            else:
                design['function'] = control.form_control_function1 or 'NONE'
        
        elif control.type.lower() == 'combobox':
            design.update({
                'items': control.list_values.split(',') if control.list_values else [],
                'font_size': int(control.font_size) if control.font_size else 12,
                'function': control.form_control_function1 or None,
                'function1': control.form_control_function1 or None,
                'function2': control.form_control_function2 or None,
                'type_name': control.type
            })
        
        elif control.type.lower() == 'numpad':
            design.update({
                'function': control.form_control_function1 or 'NONE'
            })
        
        elif control.type.lower() == 'payment_list':
            design.update({
                'function': control.form_control_function1 or None
            })
        
        elif control.type.lower() == 'sale_list':
            design.update({
                'function': control.form_control_function1 or None
            })
        
        return design
    
    def _find_control_by_id(self, control_id):
        """
        Find a control by its ID.
        
        Args:
            control_id (UUID): The control ID to find
            
        Returns:
            FormControl or None: The found control or None
        """
        for control in self.controls:
            if control.id == control_id:
                return control
        return None
    
    def _get_default_settings(self):
        """
        Get default settings when no form is loaded.
        
        Returns:
            dict: Default form settings
        """
        return {
            'name': 'SaleFlex',
            'functionality': 'NONE',
            'login_required': False,
            'toolbar': False,
            'statusbar': False,
            'background_color': 0xFFFFFF,
            'foreground_color': 0x000000,
            'width': 1024,
            'height': 768
        }
    
    @staticmethod
    def get_startup_form():
        """
        Get the startup form from database.
        
        Returns:
            Form or None: The startup form, or None if not found
        """
        # Get forms marked as startup, ordered by ID
        startup_forms = Form.filter_by(is_startup=True, is_deleted=False)
        
        if startup_forms and len(startup_forms) > 0:
            # Sort by ID to ensure consistent ordering
            startup_forms.sort(key=lambda f: str(f.id))
            return startup_forms[0]
        
        # Fallback: try to find login form by name using FormName enum
        login_forms = Form.filter_by(name=FormName.LOGIN.name, is_deleted=False)
        if login_forms and len(login_forms) > 0:
            return login_forms[0]
        
        return None


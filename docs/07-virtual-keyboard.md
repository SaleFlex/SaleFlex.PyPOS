# Virtual Keyboard Configuration

## Overview

The SaleFlex POS system supports **database-driven virtual keyboard configuration**. All visual aspects of the virtual keyboard (colors, sizes, fonts, etc.) are stored in the database and can be customized without changing code.

## Features

- **Dynamic Configuration**: All keyboard settings loaded from database  
- **Multiple Themes**: Switch between different keyboard themes instantly  
- **Enable/Disable**: Toggle virtual keyboard on/off (use physical keyboard when disabled)  
- **Hot Reload**: Settings can be reloaded without restarting the application  
- **Fully Customizable**: Font, colors, button sizes, spacing, and more  

## Database Model

### PosVirtualKeyboard Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | String | Theme name (e.g., "DEFAULT_VIRTUAL_KEYBOARD") |
| `is_active` | Boolean | **Controls if virtual keyboard is shown** |
| `keyboard_width` | Integer | Total keyboard width in pixels |
| `keyboard_height` | Integer | Total keyboard height in pixels |
| `x_position` | Integer | X position (0 = auto-center) |
| `y_position` | Integer | Y position (0 = bottom) |
| `font_family` | String | Button font family |
| `font_size` | Integer | Button font size |
| `button_width` | Integer | Regular button width |
| `button_height` | Integer | Regular button height |
| `button_min_width` | Integer | Min button width |
| `button_max_width` | Integer | Max button width |
| `button_min_height` | Integer | Min button height |
| `button_max_height` | Integer | Max button height |
| `button_background_color` | String | Button background (supports gradients) |
| `button_pressed_color` | String | Button color when pressed |
| `button_border_color` | String | Button border color |
| `button_border_width` | Integer | Border width in pixels |
| `button_border_radius` | Integer | Border radius for rounded corners |
| `space_button_min_width` | Integer | Space bar minimum width |
| `space_button_max_width` | Integer | Space bar maximum width |
| `special_button_min_width` | Integer | Backspace/Enter min width |
| `special_button_max_width` | Integer | Backspace/Enter max width |
| `control_button_width` | Integer | Caps/Sym/Close button width |
| `control_button_active_color` | String | Color when Caps/Sym is active |
| `button_text_color` | String | Optional text color |
| `button_text_color_pressed` | String | Optional text color when pressed |

## Pre-installed Themes

### 1. DEFAULT_VIRTUAL_KEYBOARD (Active by default)
- **Size**: 970x315 pixels
- **Theme**: Light gradient
- **Font**: Noto Sans CJK JP, 20px
- **Best for**: Standard touchscreen displays

### 2. DARK_THEME_KEYBOARD
- **Size**: 970x315 pixels
- **Theme**: Dark gradient
- **Font**: Noto Sans CJK JP, 20px
- **Best for**: Night mode or dark UI themes

### 3. COMPACT_KEYBOARD
- **Size**: 750x250 pixels
- **Theme**: Light gradient (smaller)
- **Font**: Noto Sans CJK JP, 16px
- **Best for**: Smaller screens or when space is limited

## How to Use

### Using the Test Script

Run the interactive test script:

```bash
python test_virtual_keyboard_settings.py
```

This provides a menu to:
1. View all keyboard themes
2. Switch between themes
3. Create custom themes
4. Disable virtual keyboard

### Programmatic Usage

#### Enable/Disable Virtual Keyboard

```python
from data_layer.engine import Engine
from data_layer.model.definition import PosVirtualKeyboard

# Disable virtual keyboard (use physical keyboard)
with Engine().get_session() as session:
    keyboards = session.query(PosVirtualKeyboard).all()
    for kb in keyboards:
        kb.is_active = False
    session.commit()

# Enable specific theme
with Engine().get_session() as session:
    theme = session.query(PosVirtualKeyboard).filter_by(
        name="DEFAULT_VIRTUAL_KEYBOARD"
    ).first()
    theme.is_active = True
    session.commit()
```

#### Switch Themes

```python
from user_interface.control.virtual_keyboard import KeyboardSettingsLoader

# Reload settings (use after making database changes)
KeyboardSettingsLoader.reload_settings()

# Check if keyboard is enabled
is_enabled = KeyboardSettingsLoader.is_keyboard_enabled()
```

#### Create Custom Theme

```python
from data_layer.engine import Engine
from data_layer.model.definition import PosVirtualKeyboard

with Engine().get_session() as session:
    custom = PosVirtualKeyboard(
        name="MY_CUSTOM_THEME",
        is_active=False,  # Don't activate yet
        keyboard_width=800,
        keyboard_height=280,
        font_family="Arial",
        font_size=18,
        button_width=70,
        button_height=35,
        button_background_color="rgb(220, 220, 220)",
        button_pressed_color="rgb(50, 150, 250)",
        button_border_color="#888888",
        button_border_width=2,
        button_border_radius=6,
        # ... set other properties as needed
    )
    session.add(custom)
    session.commit()
```

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────┐
│                  Application Start                   │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│          db_initializer.init_db()                    │
│  - Creates tables                                    │
│  - Inserts initial data                              │
│  - Initializes KeyboardSettingsLoader                │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│       KeyboardSettingsLoader.initialize()            │
│  - Connects to database                              │
│  - Loads active keyboard settings                    │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│     AlphaNumericVirtualKeyboard.display()            │
│  - Checks if keyboard is enabled                     │
│  - Loads settings from KeyboardSettingsLoader        │
│  - Creates KeyboardButton with settings              │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│            KeyboardButton.__init__()                 │
│  - Applies styles from database settings             │
│  - Uses fallback styles if settings unavailable     │
└─────────────────────────────────────────────────────┘
```

### Files Changed/Created

**New Files:**
- `data_layer/model/definition/pos_virtual_keyboard.py` - Database model
- `data_layer/db_init_data/pos_virtual_keyboard.py` - Initial data
- `user_interface/control/virtual_keyboard/keyboard_settings_loader.py` - Settings loader
- `test_virtual_keyboard_settings.py` - Test/demo script

**Modified Files:**
- `data_layer/model/definition/__init__.py` - Added PosVirtualKeyboard import
- `data_layer/db_init_data/__init__.py` - Added keyboard settings initialization
- `data_layer/db_initializer.py` - Initialize KeyboardSettingsLoader
- `user_interface/control/virtual_keyboard/__init__.py` - Export KeyboardSettingsLoader
- `user_interface/control/virtual_keyboard/keyboard_button.py` - Use database settings
- `user_interface/control/virtual_keyboard/alphanumeric_virtual_keyboard.py` - Load and apply settings

## Benefits

### For End Users
- Customize keyboard appearance without developer help
- Switch themes instantly (light/dark/compact)
- Disable virtual keyboard when using physical keyboard
- Adjust keyboard size for different screen sizes

### For Developers
- No hardcoded styles in the code
- Easy to add new themes via database
- Settings centralized in one model
- Backward compatible (fallback to defaults if DB unavailable)

## Examples

### Example 1: Restaurant POS (Large Touchscreen)
```python
# Use DEFAULT_VIRTUAL_KEYBOARD (970x315px)
# Good for 15" or larger touchscreens
activate_keyboard_theme("DEFAULT_VIRTUAL_KEYBOARD")
```

### Example 2: Retail POS (Small Touchscreen)
```python
# Use COMPACT_KEYBOARD (750x250px)
# Good for 10-12" touchscreens
activate_keyboard_theme("COMPACT_KEYBOARD")
```

### Example 3: Night Shift / Dark Mode
```python
# Use DARK_THEME_KEYBOARD
# Easier on eyes in low-light environments
activate_keyboard_theme("DARK_THEME_KEYBOARD")
```

### Example 4: Physical Keyboard Available
```python
# Disable virtual keyboard entirely
disable_virtual_keyboard()
```

## Future Enhancements

Potential future improvements:
- [ ] Multiple keyboard layouts (QWERTY, AZERTY, numeric-only)
- [ ] Language-specific keyboards
- [ ] Animation settings
- [ ] Sound effects on key press
- [ ] Keyboard layout editor UI
- [ ] Import/export themes

---

[← Back to Table of Contents](README.md) | [Previous: Dynamic Forms System](06-dynamic-forms.md) | [Next: Data Caching Strategy →](08-data-caching.md)


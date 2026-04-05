# Virtual Keyboard Configuration

The SaleFlex POS system supports **database-driven virtual keyboard configuration**. All visual aspects (colours, sizes, fonts) are stored in the database and can be customized without changing code.

---

## Features

- **Dynamic Configuration**: All keyboard settings loaded from the `PosVirtualKeyboard` table
- **Multiple Themes**: Switch between themes without restarting the application
- **Enable / Disable**: Toggle the keyboard off when a physical keyboard is attached
- **Hot Reload**: `KeyboardSettingsLoader.reload_settings()` applies changes at runtime
- **Fully Customizable**: Font, colours, button sizes, spacing, and more

---

## `PosVirtualKeyboard` Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Theme name (e.g. `"DEFAULT_VIRTUAL_KEYBOARD"`) |
| `is_active` | Boolean | **Master switch** — only the active record is used |
| `keyboard_width` | Integer | Total keyboard width in pixels |
| `keyboard_height` | Integer | Total keyboard height in pixels |
| `x_position` | Integer | X position (0 = auto-centre) |
| `y_position` | Integer | Y position (0 = bottom of screen) |
| `font_family` | String | Button font family |
| `font_size` | Integer | Button font size |
| `button_width` | Integer | Regular button width |
| `button_height` | Integer | Regular button height |
| `button_background_color` | String | Button background (supports CSS gradient strings) |
| `button_pressed_color` | String | Button colour when pressed |
| `button_border_color` | String | Button border colour |
| `button_border_width` | Integer | Border width in pixels |
| `button_border_radius` | Integer | Border radius for rounded corners |
| `space_button_min_width` | Integer | Space bar minimum width |
| `special_button_min_width` | Integer | Backspace / Enter minimum width |
| `control_button_width` | Integer | Caps / Sym / Close button width |
| `control_button_active_color` | String | Colour when Caps or Sym is active |
| `button_text_color` | String | Optional text colour |
| `button_text_color_pressed` | String | Optional text colour when pressed |

---

## Pre-installed Themes

### 1. `DEFAULT_VIRTUAL_KEYBOARD` (active by default)

- **Size**: 970 × 315 px
- **Theme**: Light gradient
- **Font**: Noto Sans CJK JP, 20 px
- **Best for**: Standard touchscreen displays (15″ or larger)

### 2. `DARK_THEME_KEYBOARD`

- **Size**: 970 × 315 px
- **Theme**: Dark gradient
- **Font**: Noto Sans CJK JP, 20 px
- **Best for**: Night shift or dark UI themes

### 3. `COMPACT_KEYBOARD`

- **Size**: 750 × 250 px
- **Theme**: Light gradient (smaller)
- **Font**: Noto Sans CJK JP, 16 px
- **Best for**: 10–12″ touchscreens or when screen space is limited

---

## How to Change the Active Theme

### Interactive test script

```bash
python test_virtual_keyboard_settings.py
```

The script provides a menu to view themes, switch between them, create custom themes, and disable the keyboard.

### Programmatic — switch theme

```python
from data_layer.engine import Engine
from data_layer.model.definition import PosVirtualKeyboard

with Engine().get_session() as session:
    # Deactivate all themes
    for kb in session.query(PosVirtualKeyboard).all():
        kb.is_active = False
    # Activate the desired theme
    theme = session.query(PosVirtualKeyboard).filter_by(
        name="DARK_THEME_KEYBOARD"
    ).first()
    theme.is_active = True
    session.commit()
```

### Programmatic — disable virtual keyboard

```python
with Engine().get_session() as session:
    for kb in session.query(PosVirtualKeyboard).all():
        kb.is_active = False
    session.commit()
```

### Reload settings at runtime

```python
from user_interface.control.virtual_keyboard import KeyboardSettingsLoader

KeyboardSettingsLoader.reload_settings()
is_enabled = KeyboardSettingsLoader.is_keyboard_enabled()
```

---

## Creating a Custom Theme

```python
from data_layer.engine import Engine
from data_layer.model.definition import PosVirtualKeyboard

with Engine().get_session() as session:
    custom = PosVirtualKeyboard(
        name="MY_CUSTOM_THEME",
        is_active=False,
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
    )
    session.add(custom)
    session.commit()
```

---

## Architecture

```
Application Start
      │
      ▼
db_initializer.init_db()
  └─ KeyboardSettingsLoader.initialize()
        └─ Loads active PosVirtualKeyboard row from DB
              │
              ▼
AlphaNumericVirtualKeyboard.display()
  ├─ Checks is_active flag
  ├─ Loads settings from KeyboardSettingsLoader
  └─ Creates KeyboardButton widgets with DB-sourced styles
```

Key implementation files:

| File | Role |
|------|------|
| `data_layer/model/definition/pos_virtual_keyboard.py` | DB model |
| `data_layer/db_init_data/pos_virtual_keyboard.py` | Seed data (3 built-in themes) |
| `user_interface/control/virtual_keyboard/keyboard_settings_loader.py` | Singleton settings cache |
| `user_interface/control/virtual_keyboard/alphanumeric_virtual_keyboard.py` | Keyboard widget (reads settings) |
| `user_interface/control/virtual_keyboard/keyboard_button.py` | Individual key widget |
| `user_interface/control/virtual_keyboard/key_press_handler_thread.py` | Non-blocking key processing |
| `user_interface/control/virtual_keyboard/key_animation_thread.py` | Key press animation |

---

## Panel-Contained Textboxes

Virtual keyboard works automatically with textboxes inside **Panel** controls:

- Focus events propagate correctly through `QScrollArea`
- Keyboard position is calculated using **global** widget coordinates (accounts for panel scroll offset)
- No additional configuration required for panel children

---

## Future Enhancements

- [ ] Multiple keyboard layouts (QWERTY, AZERTY, numeric-only)
- [ ] Language-specific keyboards
- [ ] Animation settings
- [ ] Keyboard layout editor UI
- [ ] Import/export theme profiles

---

[← Back to Table of Contents](README.md) | [Previous: First Login](05-first-login.md) | [Next: Sale Transactions →](10-sale-transactions.md)

# Installation Guide

## Step 1: Install Python

1. Visit the [Python downloads page](https://www.python.org/downloads/) and download Python 3.13 or higher.
2. Run the installer and make sure to check "Add Python to PATH" during installation.
3. Verify the installation by opening a command prompt or terminal and typing:
   ```
   python --version
   ```
   You should see the Python version displayed.

## Step 2: Download SaleFlex.PyPOS

1. Visit the [SaleFlex.PyPOS GitHub repository](https://github.com/SaleFlex/SaleFlex.PyPOS).
2. Click the green "Code" button and select "Download ZIP".
3. Extract the ZIP file to a location of your choice (e.g., `D:\GitHub.Projects\` or your home directory).

## Step 3: Set up the Virtual Environment

1. Open a command prompt or terminal.
2. Navigate to the SaleFlex.PyPOS folder you extracted:
   ```
   cd path\to\SaleFlex.PyPOS
   ```
3. Create a virtual environment:
   
   For Windows:
   ```
   python -m venv venv
   ```
   
   For macOS/Linux:
   ```
   python3 -m venv venv
   ```

4. Activate the virtual environment:
   
   For Windows:
   ```
   venv\Scripts\activate.bat
   ```
   
   For macOS/Linux:
   ```
   source venv/bin/activate
   ```

## Step 4: Install Dependencies

With the virtual environment activated, install required packages:

```bash
pip install -r requirements.txt
```

## Step 5: Run the Application

1. With the virtual environment activated, run the application:
   
   For Windows:
   ```
   python saleflex.py
   ```
   
   For macOS/Linux:
   ```
   python3 saleflex.py
   ```

2. The SaleFlex.PyPOS application should now start and display the login screen.

## Configuration

- Edit `settings.toml` to configure database connections and basic application settings
- **Note**: Many POS settings (hardware ports, display settings, backend connections, device information) are now managed through the database (`PosSettings` model) and are automatically initialized on first run
- The application uses SQLite by default, stored in `db.sqlite3`
- Device information (serial number, OS) is automatically detected using the `pos.hardware.device_info` module

---

[← Back to Table of Contents](README.md) | [Previous: System Requirements](02-system-requirements.md) | [Next: First Login →](04-first-login.md)


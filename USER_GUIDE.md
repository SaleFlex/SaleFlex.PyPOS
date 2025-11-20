# SaleFlex.PyPOS User Guide

## Introduction

SaleFlex.PyPOS is a modern point-of-sale application designed for retail stores, restaurants, and service-oriented businesses. This touch-screen enabled POS system streamlines sales transactions, inventory management, and customer relationship management in a user-friendly interface.

This guide will help you install and get started with SaleFlex.PyPOS.

## System Requirements

### Hardware Requirements
- Touch Screen Device running Windows or Linux
- Optional: Secondary customer-facing display
- ESC/P compatible receipt printer
- 2D/3D barcode scanner
- Weighing scale (optional)

### Software Requirements
- Python 3.13 or higher
- Internet connection for installation
- Operating System: Windows 10/11 or Linux

## Installation Guide

### Step 1: Install Python

1. Visit the [Python downloads page](https://www.python.org/downloads/) and download Python 3.13 or higher.
2. Run the installer and make sure to check "Add Python to PATH" during installation.
3. Verify the installation by opening a command prompt or terminal and typing:
   ```
   python --version
   ```
   You should see the Python version displayed.

### Step 2: Download SaleFlex.PyPOS

1. Visit the [SaleFlex.PyPOS GitHub repository](https://github.com/SaleFlex/SaleFlex.PyPOS).
2. Click the green "Code" button and select "Download ZIP".
3. Extract the ZIP file to a location of your choice (e.g., `D:\GitHub.Projects\` or your home directory).

### Step 3: Set up the Virtual Environment

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

### Step 4: Run the Application

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

## First Login

Upon first launch, you will be presented with a login screen. Use the following default credentials:

- **Username:** admin
- **Password:** admin

> **Important:** For security reasons, please change the default administrator password after your first login.

## Basic Navigation

### Main Menu

After logging in, you'll see the main menu with options for:

- Sales: Process transactions and orders
- Closure: End-of-day operations and cash drawer reconciliation
- Configuration: System settings and customization
- Logout: Exit current user session

### Using the NumPad

The NumPad interface allows for quick numeric input:

1. Tap the digits to enter numbers
2. Use "Backspace" to delete the last character
3. "Clear" will reset the entire input
4. "Enter" confirms your entry

### Processing a Sale

1. From the main menu, select "Sales"
2. Scan products using a barcode scanner or enter item codes manually using the NumPad
3. Adjust quantities as needed
4. When all items are added, complete the transaction
5. Print a receipt for the customer

## Troubleshooting

If you encounter issues during installation or operation:

1. Ensure all system requirements are met
2. Check that Python is correctly installed and in your PATH
3. Verify that the virtual environment is activated before running the application
4. For database connection errors, ensure your database server (if using external DB) is running

## Support and Resources

For additional help and resources:

- Visit the [SaleFlex.PyPOS GitHub repository](https://github.com/SaleFlex/SaleFlex.PyPOS)
- Review the README.md file for the latest information
- Contact the development team for technical support

## Legal Information

SaleFlex.PyPOS is free software licensed under the MIT License.

Copyright (c) 2025 Ferhat Mousavi 
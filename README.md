> **Under development. The project is not working properly yet.**

![Python 3.11](https://img.shields.io/badge/python-%3E=_3.13-success.svg)

# SaleFlex.PyPOS

### SaleFlexTouch Screen Point-of-Sale Application

SaleFlex.PyPOS (point of sale app) system is a computerized system used to process sales transactions in a retail or other business setting. The regular POS system typically includes a computer or other device, a display screen, a keyboard or touch screen, a printer for receipts, and a scanner for reading barcodes. SaleFlex.PyPOS could be run on any device that have proper components.

SaleFlex.PyPOS POS system is designed to streamline the sales process and improve efficiency. They can handle tasks such as:

- Accepting various forms of payment, including cash, credit cards, debit cards, and mobile payments.
- Generating receipts and invoices.
- Tracking inventory levels and alerting store staff when stock is running low.
- Storing customer information and preferences.
- Generating reports and analytics on sales, inventory, and customer behavior.
- Integrating with other systems, such as accounting software or a warehouse management system.

SaleFlex.PyPOS POS system can be used in a variety of businesses, including retail stores, restaurants, and other service-oriented businesses. SaleFlex.PyPOS POS system also offer additional features and capabilities, such as the ability to process returns and exchanges, track employee time and attendance, and manage customer loyalty programs.

SaleFlex.PyPOS POS is indented to respond to the needs of retail stores, fast-food restaurants as well as of a chain of restaurants. It includes the features to manage daily sales operations as well as a customized view for managers and authorized staff to track statistics, update prices and products. It has a user-friendly interface, mainly oriented to using screen and minimum keyboard input, very easy to use and It provides a lot of flexibility and maintainability. It is designed as that expansion might happen. 

It has modules for easily integrate it to different payment systems, loyalty systems, printers and backend systems.

### SaleFlex.GATE Integration

SaleFlex.PyPOS is designed to work seamlessly with **SaleFlex.GATE** - a centralized management system for businesses operating across multiple locations. SaleFlex.GATE serves as a control hub that provides:

- **Centralized Management:** Manage and monitor multiple SaleFlex.PyPOS systems from one location with real-time insights
- **Cloud-Based Access:** Remote control of operations for business owners and managers
- **ERP Integration:** Seamless connection with existing ERP systems to ensure data synchronization
- **Scalable Architecture:** Support for growing businesses with increasing numbers of stores and POS systems

SaleFlex.GATE uses Django and Django REST Framework to deliver robust backend services, allowing for efficient data flow between your POS terminals and enterprise software.

For more details, visit the [SaleFlex.GATE](https://github.com/SaleFlex/SaleFlex.GATE) project repository.

> ### Project Requirements
>
> ##### Hardware Requirements
>
> - Linux/Windows supported Touch Screen Devices (with one or two displays) 
> - ESC/P printers
> - 2D and 3D barcode readers 
> - Weighing Scales
>
> ##### Software Requirements
>
> - Python 3.13
> - PySide6 6.9.0
> - SQLAlchemy 2.0.40
> - requests 2.32.3
>
> #### Supported Database Engines
>
> - SQLite
> - Postgresql
> - MySQL
> - Oracle
> - MS-SQL
> - Firebird
> - Sybase

### Installation Methods

* Install [Python 3.13](https://www.python.org/downloads/) on your system.
* Download SaleFlex.PyPOS project on your system.
* Run `python3 -m venv venv` on SaleFlex.PyPOS project folder. This will create the venv directory on your project folder, and also create directories inside it containing a copy of the Python interpreter and various supporting files.
* For Windows:
  * First run `venv\Scripts\activate.bat` for activating your virtual environment. This will install proper packages.
  * Then run `python saleflex.py`
* For MacOS or Linux:
  * First run `source  venv\Scripts\activate` for activating your virtual environment. This will install proper packages.
  * Then run `python3 saleflex.py`
* With the execution of these commands, the SaleFlex.PyPOS application will start.

### Project Roadmap

- [ ] Database Structure
- [ ] POS Manager Module
- [ ] User Interface Modules:
  - [ ] Dynamic Interface Interpreter Module
  - [ ] Interface Functions
  - [ ] Tables Layout Module
- [ ] SPU/PLU Management Module
- [ ] Customer Module
- [ ] Printer Module
- [ ] Payment Module
- [ ] Loyalty Module
- [ ] SaleFlex.GATE Integration Module:
  - [ ] Data Synchronization Service
  - [ ] ERP Connection Layer
  - [ ] Multi-Store Management
  - [ ] Cloud-Based Remote Access
- [ ] Campaign Module
- [ ] Reports Module
- [ ] Screen Designer App

### Contributors

<table>
<tr>
    <td align="center">
        <a href="https://github.com/ferhat-mousavi">
            <img src="https://avatars.githubusercontent.com/u/5930760?v=4" width="100;" alt="Ferhat Mousavi"/>
            <br />
            <sub><b>Ferhat Mousavi</b></sub>
        </a>
    </td>
</tr>
</table>

### Donation and Support
If you like the project and want to support it or if you want to contribute to the development of new modules, you can donate to the following crypto addresses.

- USDT: 0xa5a87a939bfcd492f056c26e4febe102ea599b5b
- BUSD: 0xa5a87a939bfcd492f056c26e4febe102ea599b5b
- BTC: 184FDZ1qV2KFzEaNqMefw8UssG8Z57FA6F
- ETH: 0xa5a87a939bfcd492f056c26e4febe102ea599b5b
- SOL: HS9dUvRSqYGxkDiwTpCvKTVBBWqqtVoXdRK2AanLHMZn
- MATIC: 0xa5a87a939bfcd492f056c26e4febe102ea599b5b
- XTZ: tz1RvnJk5xVtDy2g6ijkcyGSzKA4qFg5Nuy3




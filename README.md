![Python 3.13](https://img.shields.io/badge/python-%3E=_3.13-success.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.11.0-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.48-green.svg)
![License](https://img.shields.io/badge/license-AGPLv3-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0b8-orange.svg)
![Status](https://img.shields.io/badge/status-beta-yellow.svg)

[SaleFlex Ecosystem](https://github.com/SaleFlex) | **[SaleFlex.PyPOS](https://github.com/SaleFlex/SaleFlex.PyPOS)** | [SaleFlex.OFFICE](https://github.com/SaleFlex/SaleFlex.OFFICE) | [SaleFlex.GATE](https://github.com/SaleFlex/SaleFlex.GATE) | [SaleFlex.KITCHEN](https://github.com/SaleFlex/SaleFlex.KITCHEN) | [SaleFlex.mPOS](https://github.com/SaleFlex/SaleFlex.mPOS)

# SaleFlex.PyPOS

**SaleFlex.PyPOS** is a modern, open-source point-of-sale terminal built with Python and PySide6 (Qt). It runs on standard touch-screen hardware, works fully offline, and connects to SaleFlex.OFFICE or SaleFlex.GATE when you are ready to scale.

Whether you run a single shop or a chain of stores, PyPOS gives your cashiers a fast, touch-optimised interface for sales, payments, closures, inventory, and customer loyalty - right out of the box.

> Developed and operated by **[Mousavi.Tech](https://mousavi.tech)**

---

## Who Is This For?

SaleFlex.PyPOS is built for:

- **Retailers and restaurateurs** who need a self-hosted, open-source POS terminal they can run on their own hardware without monthly fees.
- **Developers and integrators** who want a Python-based POS they can extend with custom modules, ERP connectors, or payment gateways.
- **Small and medium businesses** looking for a flexible alternative to expensive proprietary POS systems.
- **Tech-forward teams** who want full control over their data, peripherals, and integrations - without vendor lock-in.

---

## Community Edition

SaleFlex.PyPOS is fully **free and open source** under the [GNU Affero General Public License v3.0 (AGPLv3)](LICENSE).

The Community Edition includes everything you need to run a complete POS operation:

- Touch-optimised sale screen with NumPad, PLU/barcode lookup, and line management
- Multi-payment processing (cash, card, mobile pay, split tender, loyalty points)
- End-of-day closure with Z-report and receipt printer output
- Customer management with loyalty points, tiers, and activity history
- Campaign and promotion engine (basket, product, time-based, buy-X-get-Y, payment discounts)
- Inventory management with stock-in, adjustment, and movement history
- Cashier management with role-based access control
- Offline-first - works without internet; syncs when connected
- SaleFlex.OFFICE and SaleFlex.GATE integration for multi-store operations
- Self-hosted - your data stays with you

Anyone can clone, run, and modify SaleFlex.PyPOS for their own needs. Contributions are welcome.

---

## Commercial Services

Need professional support or custom features? We offer:

- **Custom development** - tailored features, integrations, and workflows built for your business.
- **Implementation & onboarding** - hands-on setup, hardware configuration, and staff training.
- **Priority support** - dedicated support channels with guaranteed response times.
- **Integration services** - connecting PyPOS to your existing ERP, accounting, loyalty, or payment systems.
- **Fiscal compliance** - country-specific fiscal printer and e-invoice integrations.

> Contact us at [saleflex.pro](https://saleflex.pro) for commercial enquiries.

---

## Managed Cloud

Pair SaleFlex.PyPOS with **SaleFlex Cloud** (coming soon) for a fully managed backend:

- No server to manage - we handle updates, backups, and scaling.
- One-click OFFICE and GATE backend provisioning.
- Built-in sales, stock, and KPI reporting dashboards.
- Enterprise-grade security and compliance.
- Multi-region availability.

> Join the waitlist at [saleflex.net](https://saleflex.net) to be notified when Managed Cloud launches.

---

## Download Ready Builds

Pre-packaged installers for Windows and Linux are currently in preparation.

**Until then, get started in minutes:**

```bash
git clone https://github.com/SaleFlex/SaleFlex.PyPOS.git
cd SaleFlex.PyPOS

# Windows
python -m venv venv
venv\Scripts\activate.bat

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python saleflex.py
```

**Default login credentials:**

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin` | Administrator |
| `jdoe` | `1234` | Standard cashier |

> **Requirements:** Python 3.13+ - PySide6 6.11+ - SQLAlchemy 2.0+ - Windows or Linux

---

## Screenshots

**Login Screen**
![Login Screen](static_files/images/sample_login.jpg)

**Main Menu**
![Main Menu](static_files/images/sample_main_menu.jpg)

**Sale Screen**
![Sale Form](static_files/images/sample_sale_form.jpg)

**Payment Screen**
![Payment Form](static_files/images/sample_sale_payment_form.jpg)

**End-of-Day Closure**
![Closure Form](static_files/images/sample_closure_form.jpg)

**Closure Detail**
![Closure Detail](static_files/images/sample_closure_detail_form.jpg)

**Product List**
![Product List](static_files/images/sample_product_form.jpg)

**Customer Management**
![Customer List](static_files/images/sample_customer_list_form.jpg)

**Warehouse Management**
![Warehouse List](static_files/images/sample_warehouse_list_form.jpg)

---

## Demo Video

[Watch Demo - v1.0.0b8](https://youtu.be/HoA2p6M8fuM)

> More videos covering the full workflow are being prepared and will be published on the SaleFlex YouTube channel shortly.

---

## Roadmap

### Done
- Touch-optimised POS interface (PySide6, landscape tablet and desktop)
- Cashier login with role-based access control
- Sale screen with NumPad, PLU/barcode lookup, item discounts and markups
- Multi-payment processing with split tender and change calculation
- Campaign and promotion engine (basket, product, time-based, buy-X-get-Y, payment discounts, coupons)
- Customer management with phone-based loyalty, tiered points, earn and redeem
- End-of-day closure with Z-report, receipt printer output, and closure history
- Product management with tabbed detail view (info, barcodes, attributes, variants)
- Inventory management (stock-in, adjustment, movement history, low-stock alerts)
- Cashier management (create, edit, role permissions)
- Dynamic form rendering system (100+ DB-driven UI forms)
- SaleFlex.OFFICE integration (data sync, transaction and closure push, offline retry)
- SaleFlex.GATE integration foundation
- Offline outbox with automatic retry
- Central logging and typed exception hierarchy
- Single-instance lock and startup guards

### In Progress
- Settings screen (POS, loyalty, campaign management via UI)
- DataStore-based settings persistence

### Planned
- Pre-packaged Windows and Linux installers
- Restaurant table management
- Kitchen display system (KDS) integration
- Fiscal printer and e-invoice support (Turkey, EU, USA)
- Barcode scanner and receipt printer hardware drivers
- Multi-language support
- Advanced reporting and analytics
- Multi-store and multi-terminal management
- SaleFlex Cloud (managed hosting)

---

## Related Projects

| Project | Description |
|---------|-------------|
| [SaleFlex.OFFICE](https://github.com/SaleFlex/SaleFlex.OFFICE) | Back-office and ERP-style management |
| [SaleFlex.GATE](https://github.com/SaleFlex/SaleFlex.GATE) | Central hub and API gateway |
| [SaleFlex.KITCHEN](https://github.com/SaleFlex/SaleFlex.KITCHEN) | Kitchen display system |
| [SaleFlex.mPOS](https://github.com/SaleFlex/SaleFlex.mPOS) | Android mobile POS |
| [SaleFlex.POS](https://github.com/SaleFlex/SaleFlex.POS) | Legacy .NET POS client |

---

## License

This project is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](LICENSE) for details.

---

## Contributors

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

## Donation and Support

If you find SaleFlex.PyPOS useful and want to support its development:

- **USDT / BUSD / ETH:** `0xa5a87a939bfcd492f056c26e4febe102ea599b5b`
- **BTC:** `15qyZpi6HjYyVhKKBsCbZSXU4bLdVJ8Phe`
- **SOL:** `Gt3bDczPcJvfBeg9TTBrBJGSHLJVkvnSSTov8W3QMpQf`
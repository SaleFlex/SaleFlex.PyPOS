"""
SaleFlex.PyPOS - Database Initial Data

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

from data_layer.model import Currency


def _insert_currencies(session):
    """Insert default currencies if not exists
    
    Returns:
        Currency: GBP Currency object, or None if currencies already exist
    """
    currency_exists = session.query(Currency).first()
    if not currency_exists:
        currencies = [
            {
                "no": 1,
                "name": "Argentine Peso",
                "currency_code": 32,
                "sign": "ARS",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1025.50,
                "decimal_places": 2
            },
            {
                "no": 2,
                "name": "Australian Dollar",
                "currency_code": 36,
                "sign": "AUD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 2.05,
                "decimal_places": 2
            },
            {
                "no": 3,
                "name": "Brazilian Real",
                "currency_code": 986,
                "sign": "BRL",
                "sign_direction": "LEFT",
                "currency_symbol": "R$",
                "rate": 7.85,
                "decimal_places": 2
            },
            {
                "no": 4,
                "name": "British Pound",
                "currency_code": 826,
                "sign": "GBP",
                "sign_direction": "LEFT",
                "currency_symbol": "£",
                "rate": 1.0,
                "decimal_places": 2
            },
            {
                "no": 5,
                "name": "Canadian Dollar",
                "currency_code": 124,
                "sign": "CAD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1.82,
                "decimal_places": 2
            },
            {
                "no": 6,
                "name": "Chilean Peso",
                "currency_code": 152,
                "sign": "CLP",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1245.80,
                "decimal_places": 0
            },
            {
                "no": 7,
                "name": "Chinese Yuan",
                "currency_code": 156,
                "sign": "CNY",
                "sign_direction": "LEFT",
                "currency_symbol": "¥",
                "rate": 9.46,
                "decimal_places": 2
            },
            {
                "no": 8,
                "name": "Colombian Peso",
                "currency_code": 170,
                "sign": "COP",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 5287.45,
                "decimal_places": 2
            },
            {
                "no": 9,
                "name": "Czech Koruna",
                "currency_code": 203,
                "sign": "CZK",
                "sign_direction": "LEFT",
                "currency_symbol": "Kč",
                "rate": 28.35,
                "decimal_places": 2
            },
            {
                "no": 10,
                "name": "Danish Krone",
                "currency_code": 208,
                "sign": "DKK",
                "sign_direction": "LEFT",
                "currency_symbol": "kr",
                "rate": 8.80,
                "decimal_places": 2
            },
            {
                "no": 11,
                "name": "Egyptian Pound",
                "currency_code": 818,
                "sign": "EGP",
                "sign_direction": "LEFT",
                "currency_symbol": "£",
                "rate": 51.15,
                "decimal_places": 2
            },
            {
                "no": 12,
                "name": "Euro",
                "currency_code": 978,
                "sign": "EUR",
                "sign_direction": "LEFT",
                "currency_symbol": "€",
                "rate": 1.18,
                "decimal_places": 2
            },
            {
                "no": 13,
                "name": "Hong Kong Dollar",
                "currency_code": 344,
                "sign": "HKD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 10.22,
                "decimal_places": 2
            },
            {
                "no": 14,
                "name": "Hungarian Forint",
                "currency_code": 348,
                "sign": "HUF",
                "sign_direction": "LEFT",
                "currency_symbol": "Ft",
                "rate": 461.75,
                "decimal_places": 2
            },
            {
                "no": 15,
                "name": "Indian Rupee",
                "currency_code": 356,
                "sign": "INR",
                "sign_direction": "LEFT",
                "currency_symbol": "₹",
                "rate": 110.85,
                "decimal_places": 2
            },
            {
                "no": 16,
                "name": "Indonesian Rupiah",
                "currency_code": 360,
                "sign": "IDR",
                "sign_direction": "LEFT",
                "currency_symbol": "Rp",
                "rate": 20586.75,
                "decimal_places": 2
            },
            {
                "no": 17,
                "name": "Iranian Rial",
                "currency_code": 364,
                "sign": "IRR",
                "sign_direction": "LEFT",
                "currency_symbol": "﷼",
                "rate": 55000.0,
                "decimal_places": 2
            },
            {
                "no": 18,
                "name": "Iraqi Dinar",
                "currency_code": 368,
                "sign": "IQD",
                "sign_direction": "LEFT",
                "currency_symbol": "د.ع",
                "rate": 1713.75,
                "decimal_places": 3
            },
            {
                "no": 19,
                "name": "Israeli Shekel",
                "currency_code": 376,
                "sign": "ILS",
                "sign_direction": "LEFT",
                "currency_symbol": "₪",
                "rate": 4.72,
                "decimal_places": 2
            },
            {
                "no": 20,
                "name": "Japanese Yen",
                "currency_code": 392,
                "sign": "JPY",
                "sign_direction": "LEFT",
                "currency_symbol": "¥",
                "rate": 193.45,
                "decimal_places": 0
            },
            {
                "no": 21,
                "name": "Kuwaiti Dinar",
                "currency_code": 414,
                "sign": "KWD",
                "sign_direction": "LEFT",
                "currency_symbol": "د.ك",
                "rate": 0.40,
                "decimal_places": 3
            },
            {
                "no": 22,
                "name": "Malaysian Ringgit",
                "currency_code": 458,
                "sign": "MYR",
                "sign_direction": "LEFT",
                "currency_symbol": "RM",
                "rate": 5.89,
                "decimal_places": 2
            },
            {
                "no": 23,
                "name": "Mexican Peso",
                "currency_code": 484,
                "sign": "MXN",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 26.42,
                "decimal_places": 2
            },
            {
                "no": 24,
                "name": "New Zealand Dollar",
                "currency_code": 554,
                "sign": "NZD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 2.21,
                "decimal_places": 2
            },
            {
                "no": 25,
                "name": "Norwegian Krone",
                "currency_code": 578,
                "sign": "NOK",
                "sign_direction": "LEFT",
                "currency_symbol": "kr",
                "rate": 14.86,
                "decimal_places": 2
            },
            {
                "no": 26,
                "name": "Philippine Peso",
                "currency_code": 608,
                "sign": "PHP",
                "sign_direction": "LEFT",
                "currency_symbol": "₱",
                "rate": 73.62,
                "decimal_places": 2
            },
            {
                "no": 27,
                "name": "Polish Zloty",
                "currency_code": 985,
                "sign": "PLN",
                "sign_direction": "LEFT",
                "currency_symbol": "zł",
                "rate": 5.15,
                "decimal_places": 2
            },
            {
                "no": 28,
                "name": "Qatari Riyal",
                "currency_code": 634,
                "sign": "QAR",
                "sign_direction": "LEFT",
                "currency_symbol": "ر.ق",
                "rate": 4.77,
                "decimal_places": 2
            },
            {
                "no": 29,
                "name": "Romanian Leu",
                "currency_code": 946,
                "sign": "RON",
                "sign_direction": "LEFT",
                "currency_symbol": "lei",
                "rate": 5.85,
                "decimal_places": 2
            },
            {
                "no": 30,
                "name": "Russian Ruble",
                "currency_code": 643,
                "sign": "RUB",
                "sign_direction": "LEFT",
                "currency_symbol": "₽",
                "rate": 101.25,
                "decimal_places": 2
            },
            {
                "no": 31,
                "name": "Saudi Arabian Riyal",
                "currency_code": 682,
                "sign": "SAR",
                "sign_direction": "LEFT",
                "currency_symbol": "ر.س",
                "rate": 4.91,
                "decimal_places": 2
            },
            {
                "no": 32,
                "name": "Singapore Dollar",
                "currency_code": 702,
                "sign": "SGD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1.76,
                "decimal_places": 2
            },
            {
                "no": 33,
                "name": "South African Rand",
                "currency_code": 710,
                "sign": "ZAR",
                "sign_direction": "LEFT",
                "currency_symbol": "R",
                "rate": 24.17,
                "decimal_places": 2
            },
            {
                "no": 34,
                "name": "South Korean Won",
                "currency_code": 410,
                "sign": "KRW",
                "sign_direction": "LEFT",
                "currency_symbol": "₩",
                "rate": 1789.65,
                "decimal_places": 0
            },
            {
                "no": 35,
                "name": "Swedish Krona",
                "currency_code": 752,
                "sign": "SEK",
                "sign_direction": "LEFT",
                "currency_symbol": "kr",
                "rate": 14.72,
                "decimal_places": 2
            },
            {
                "no": 36,
                "name": "Swiss Franc",
                "currency_code": 756,
                "sign": "CHF",
                "sign_direction": "LEFT",
                "currency_symbol": "Fr",
                "rate": 1.17,
                "decimal_places": 2
            },
            {
                "no": 37,
                "name": "Thai Baht",
                "currency_code": 764,
                "sign": "THB",
                "sign_direction": "LEFT",
                "currency_symbol": "฿",
                "rate": 47.85,
                "decimal_places": 2
            },
            {
                "no": 38,
                "name": "Turkish Lira",
                "currency_code": 949,
                "sign": "TRY",
                "sign_direction": "LEFT",
                "currency_symbol": "₺",
                "rate": 35.21,
                "decimal_places": 2
            },
            {
                "no": 39,
                "name": "UAE Dirham",
                "currency_code": 784,
                "sign": "AED",
                "sign_direction": "LEFT",
                "currency_symbol": "د.إ",
                "rate": 4.81,
                "decimal_places": 2
            },
            {
                "no": 40,
                "name": "US Dollar",
                "currency_code": 840,
                "sign": "USD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1.31,
                "decimal_places": 2
            }
        ]

        gbp_currency = None
        for currency_data in currencies:
            currency = Currency(
                no=currency_data["no"],
                name=currency_data["name"],
                currency_code=currency_data["currency_code"],
                sign=currency_data["sign"],
                sign_direction=currency_data["sign_direction"],
                currency_symbol=currency_data["currency_symbol"],
                decimal_places=currency_data.get("decimal_places", 2)  # Default to 2 decimal places
            )
            session.add(currency)
            session.flush()  # Flush to get the ID
            
            # Store GBP currency for return
            if currency_data["sign"] == "GBP":
                gbp_currency = currency
        
        print("✓ Default currencies added (40 currencies)")
        return gbp_currency  # Return GBP currency for use in PosSettings
    else:
        # Currencies already exist, find and return GBP currency
        gbp_currency = session.query(Currency).filter_by(sign="GBP", is_deleted=False).first()
        return gbp_currency
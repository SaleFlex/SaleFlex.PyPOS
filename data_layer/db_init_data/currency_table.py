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

from data_layer.model import CurrencyTable, Currency


def _insert_currency_table(session, admin_cashier_id):
    """
    Insert default currency exchange rates if not exists.
    
    Creates exchange rate entries with GBP as base currency and all other
    currencies as target currencies. The rates are based on the original
    currency rates from the currency initialization data.
    
    Args:
        session: Database session
        admin_cashier_id: Admin cashier ID for audit fields
    """
    try:
        currency_table_exists = session.query(CurrencyTable).first()
        if not currency_table_exists:
            # Get GBP currency as base currency
            gbp_currency = session.query(Currency).filter_by(sign="GBP", is_deleted=False).first()
            if not gbp_currency:
                print("⚠ GBP currency not found, skipping currency table initialization")
                return
            
            # Original rates from currency init data (relative to GBP)
            # These rates represent: 1 GBP = rate * target_currency
            currency_rates = {
                "ARS": 1025.50,
                "AUD": 2.05,
                "BRL": 7.85,
                "GBP": 1.0,
                "CAD": 1.82,
                "CLP": 1245.80,
                "CNY": 9.46,
                "COP": 5287.45,
                "CZK": 28.35,
                "DKK": 8.80,
                "EGP": 51.15,
                "EUR": 1.18,
                "HKD": 10.22,
                "HUF": 461.75,
                "INR": 110.85,
                "IDR": 20586.75,
                "IRR": 55000.0,
                "IQD": 1713.75,
                "ILS": 4.72,
                "JPY": 193.45,
                "KWD": 0.40,
                "MYR": 5.89,
                "MXN": 26.42,
                "NZD": 2.21,
                "NOK": 14.86,
                "PHP": 73.62,
                "PLN": 5.15,
                "QAR": 4.77,
                "RON": 5.85,
                "RUB": 101.25,
                "SAR": 4.91,
                "SGD": 1.76,
                "ZAR": 24.17,
                "KRW": 1789.65,
                "SEK": 14.72,
                "CHF": 1.17,
                "THB": 47.85,
                "TRY": 35.21,
                "AED": 4.81,
                "USD": 1.31
            }
            
            # Create currency table entries for each currency (GBP -> other currencies)
            for sign, rate in currency_rates.items():
                if sign == "GBP":
                    continue  # Skip GBP to GBP (would be 1.0)
                
                # Find target currency by sign
                target_currency = session.query(Currency).filter_by(sign=sign, is_deleted=False).first()
                if target_currency:
                    currency_table_entry = CurrencyTable(
                        fk_base_currency_id=gbp_currency.id,
                        fk_target_currency_id=target_currency.id,
                        rate=rate
                    )
                    currency_table_entry.fk_cashier_create_id = admin_cashier_id
                    currency_table_entry.fk_cashier_update_id = admin_cashier_id
                    session.add(currency_table_entry)
            
            # Also create reverse rates (other currencies -> GBP) for convenience
            # Reverse rate = 1 / forward_rate
            for sign, rate in currency_rates.items():
                if sign == "GBP":
                    continue
                
                target_currency = session.query(Currency).filter_by(sign=sign, is_deleted=False).first()
                if target_currency and rate != 0:
                    reverse_rate = 1.0 / rate
                    currency_table_entry = CurrencyTable(
                        fk_base_currency_id=target_currency.id,
                        fk_target_currency_id=gbp_currency.id,
                        rate=reverse_rate
                    )
                    currency_table_entry.fk_cashier_create_id = admin_cashier_id
                    currency_table_entry.fk_cashier_update_id = admin_cashier_id
                    session.add(currency_table_entry)
            
            print("✓ Default currency exchange rates added")
        else:
            print("✓ Currency table already exists")
    except Exception as e:
        print(f"⚠ Error inserting currency table: {e}")
        import traceback
        traceback.print_exc()


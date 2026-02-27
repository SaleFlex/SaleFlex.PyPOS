"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from typing import Optional
from core.exceptions import TaxCalculationError



from core.logger import get_logger

logger = get_logger(__name__)

class VatService:
    """
    VAT (Value Added Tax) calculation service.
    
    This service provides centralized VAT calculation functionality with
    currency-aware rounding. All VAT calculations in the application should
    use this service to ensure consistency.
    
    The service calculates VAT using the formula:
        vat_amount = price * (vat_rate / (100 + vat_rate))
    
    Rounding is performed based on the currency's decimal_places setting:
    - If the digit after decimal_places is 5 or greater, round up
    - If the digit after decimal_places is less than 5, round down
    """
    
    @staticmethod
    def get_currency_decimal_places(currency_sign: Optional[str], product_data: Optional[dict] = None) -> int:
        """
        Get decimal places for a currency.
        
        Args:
            currency_sign: Currency sign (e.g., "GBP", "USD") or None
            product_data: Optional product_data cache dictionary. If not provided,
                         will query from database.
        
        Returns:
            int: Number of decimal places (default: 2)
        """
        if not currency_sign:
            return 2  # Default
        
        try:
            # Try to get currency from product_data cache first (more efficient)
            if product_data:
                all_currencies = product_data.get("Currency", [])
                currency = next(
                    (c for c in all_currencies 
                     if c.sign == currency_sign and not (hasattr(c, 'is_deleted') and c.is_deleted)),
                    None
                )
                if currency and currency.decimal_places is not None:
                    return currency.decimal_places
            
            # Fallback: query from database
            from data_layer.model import Currency
            currencies = Currency.filter_by(sign=currency_sign, is_deleted=False)
            if currencies and len(currencies) > 0:
                currency = currencies[0]
                if currency.decimal_places is not None:
                    return currency.decimal_places
            
            # Default if currency not found
            return 2
        except TaxCalculationError:
            raise
        except Exception as e:
            logger.error("[VAT_SERVICE] Error getting currency decimal_places: %s, defaulting to 2", e)
            return 2
    
    @staticmethod
    def round_by_currency(value: float, decimal_places: int) -> float:
        """
        Round a value according to currency decimal places.
        
        Rounding rule:
        - If the digit after decimal_places is 5 or greater, round up
        - If the digit after decimal_places is less than 5, round down
        
        Examples for decimal_places=2:
        - 1.12345 -> 1.12 (3 < 5, round down)
        - 1.65231 -> 1.65 (2 < 5, round down)
        - 1.34567 -> 1.35 (5 >= 5, round up)
        - 1.56789 -> 1.57 (7 >= 5, round up)
        
        Args:
            value: Value to round
            decimal_places: Number of decimal places to round to
        
        Returns:
            float: Rounded value
        """
        if decimal_places < 0:
            decimal_places = 0
        
        # Convert to Decimal for precise rounding
        decimal_value = Decimal(str(value))
        
        # Calculate the multiplier (10^decimal_places)
        multiplier = Decimal(10) ** decimal_places
        
        # Multiply by multiplier to shift decimal point
        shifted = decimal_value * multiplier
        
        # Get the fractional part (digit after decimal_places)
        fractional_part = shifted - shifted.quantize(Decimal('1'), rounding=ROUND_DOWN)
        
        # Check if fractional part is >= 0.5 (i.e., next digit >= 5)
        if fractional_part >= Decimal('0.5'):
            # Round up
            rounded = shifted.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        else:
            # Round down
            rounded = shifted.quantize(Decimal('1'), rounding=ROUND_DOWN)
        
        # Divide back to get final rounded value
        result = float(rounded / multiplier)
        return result
    
    @staticmethod
    def calculate_vat(price: float, vat_rate: float, currency_sign: Optional[str] = None, 
                     product_data: Optional[dict] = None) -> float:
        """
        Calculate VAT amount from price and VAT rate.
        
        Uses the formula: vat_amount = price * (vat_rate / (100 + vat_rate))
        
        The result is rounded according to the currency's decimal_places setting.
        If currency_sign is not provided, default decimal_places=2 is used.
        
        Args:
            price: Base price (including VAT)
            vat_rate: VAT rate percentage (e.g., 18.0 for 18%)
            currency_sign: Optional currency sign (e.g., "GBP", "USD") for rounding
            product_data: Optional product_data cache dictionary for currency lookup
        
        Returns:
            float: Calculated VAT amount, rounded according to currency decimal_places
        """
        if vat_rate <= 0:
            return 0.0
        
        try:
            # Calculate VAT using the formula: price * (vat_rate / (100 + vat_rate))
            vat_amount = price * (vat_rate / (100 + vat_rate))
            
            # Get decimal places for rounding
            decimal_places = VatService.get_currency_decimal_places(currency_sign, product_data)
            
            # Round according to currency decimal places
            rounded_vat = VatService.round_by_currency(vat_amount, decimal_places)
        except ZeroDivisionError as e:
            raise TaxCalculationError(
                f"Invalid VAT rate causes division by zero: rate={vat_rate}"
            ) from e
        except (TypeError, ValueError) as e:
            raise TaxCalculationError(
                f"VAT calculation failed for price={price}, rate={vat_rate}: {e}"
            ) from e
        
        return rounded_vat
    
    @staticmethod
    def calculate_vat_with_decimal_places(price: float, vat_rate: float, decimal_places: int) -> float:
        """
        Calculate VAT amount with explicit decimal places.
        
        This method is useful when you already know the decimal places value
        and want to avoid currency lookup.
        
        Args:
            price: Base price (including VAT)
            vat_rate: VAT rate percentage (e.g., 18.0 for 18%)
            decimal_places: Number of decimal places for rounding
        
        Returns:
            float: Calculated VAT amount, rounded according to decimal_places
        """
        if vat_rate <= 0:
            return 0.0
        
        try:
            # Calculate VAT using the formula: price * (vat_rate / (100 + vat_rate))
            vat_amount = price * (vat_rate / (100 + vat_rate))
            
            # Round according to specified decimal places
            rounded_vat = VatService.round_by_currency(vat_amount, decimal_places)
        except ZeroDivisionError as e:
            raise TaxCalculationError(
                f"Invalid VAT rate causes division by zero: rate={vat_rate}"
            ) from e
        except (TypeError, ValueError) as e:
            raise TaxCalculationError(
                f"VAT calculation failed for price={price}, rate={vat_rate}, "
                f"decimal_places={decimal_places}: {e}"
            ) from e
        
        return rounded_vat


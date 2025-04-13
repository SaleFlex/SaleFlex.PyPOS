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

from enum import Enum, auto


class PaymentType(Enum):
    NONE = auto()
    CASH = auto()
    CREDIT_CARD = auto()
    CHECK = auto()
    ON_CREDIT = auto()
    PREPAID_CARD = auto()
    MOBILE = auto()
    BONUS = auto()
    EXCHANGE = auto()
    CURRENT_ACCOUNT = auto()
    BANK_TRANSFER = auto()

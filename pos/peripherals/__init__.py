"""
SaleFlex.PyPOS - Point-of-sale peripherals (OPOS-style device layer).

Hardware integration is stubbed: commands are logged until drivers are added.
"""

from pos.peripherals.cash_drawer import CashDrawer, get_default_cash_drawer
from pos.peripherals.customer_display import CustomerDisplay
from pos.peripherals.line_display import LineDisplay, get_default_line_display
from pos.peripherals.pos_printer import POSPrinter, get_default_pos_printer
from pos.peripherals.remote_order_display import RemoteOrderDisplay
from pos.peripherals.scanner import Scanner
from pos.peripherals.scale import Scale

__all__ = [
    "CashDrawer",
    "CustomerDisplay",
    "LineDisplay",
    "POSPrinter",
    "RemoteOrderDisplay",
    "Scanner",
    "Scale",
    "get_default_cash_drawer",
    "get_default_line_display",
    "get_default_pos_printer",
]

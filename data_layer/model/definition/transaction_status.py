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

from enum import Enum


class TransactionStatus(Enum):
    """Enum for transaction states"""
    DRAFT = "draft"              # Draft, not yet started
    ACTIVE = "active"            # Active, products can be added
    PENDING = "pending"          # Pending, temporarily suspended
    HOLD = "hold"                # On hold, temporarily stopped
    KITCHEN = "kitchen"          # In kitchen, order being prepared
    READY = "ready"              # Ready, ready for delivery
    DELIVERED = "delivered"      # Delivered
    COMPLETED = "completed"      # Completed, payment done
    CANCELLED = "cancelled"      # Cancelled
    REFUNDED = "refunded"        # Refunded


class TransactionType(Enum):
    """Enum for transaction types"""
    SALE = "sale"                # Sale
    ORDER = "order"              # Order
    RESERVATION = "reservation"  # Reservation
    RETURN = "return"            # Return
    EXCHANGE = "exchange"        # Exchange
    QUOTE = "quote"              # Quote
    LAYAWAY = "layaway"          # Layaway sale


class KitchenOrderStatus(Enum):
    """Enum for kitchen order statuses"""
    WAITING = "waiting"          # Waiting
    PREPARING = "preparing"      # Preparing
    READY = "ready"              # Ready
    SERVED = "served"            # Served
    CANCELLED = "cancelled"      # Cancelled


class DeliveryStatus(Enum):
    """Enum for delivery statuses"""
    PENDING = "pending"          # Pending
    PREPARING = "preparing"      # Preparing
    READY = "ready"              # Ready
    OUT_FOR_DELIVERY = "out_for_delivery"  # Out for delivery
    DELIVERED = "delivered"      # Delivered
    FAILED = "failed"            # Failed
    RETURNED = "returned"        # Returned


# String constants for backward compatibility
TRANSACTION_STATUS_DRAFT = TransactionStatus.DRAFT.value
TRANSACTION_STATUS_ACTIVE = TransactionStatus.ACTIVE.value
TRANSACTION_STATUS_PENDING = TransactionStatus.PENDING.value
TRANSACTION_STATUS_HOLD = TransactionStatus.HOLD.value
TRANSACTION_STATUS_KITCHEN = TransactionStatus.KITCHEN.value
TRANSACTION_STATUS_READY = TransactionStatus.READY.value
TRANSACTION_STATUS_DELIVERED = TransactionStatus.DELIVERED.value
TRANSACTION_STATUS_COMPLETED = TransactionStatus.COMPLETED.value
TRANSACTION_STATUS_CANCELLED = TransactionStatus.CANCELLED.value
TRANSACTION_STATUS_REFUNDED = TransactionStatus.REFUNDED.value

TRANSACTION_TYPE_SALE = TransactionType.SALE.value
TRANSACTION_TYPE_ORDER = TransactionType.ORDER.value
TRANSACTION_TYPE_RESERVATION = TransactionType.RESERVATION.value
TRANSACTION_TYPE_RETURN = TransactionType.RETURN.value
TRANSACTION_TYPE_EXCHANGE = TransactionType.EXCHANGE.value
TRANSACTION_TYPE_QUOTE = TransactionType.QUOTE.value
TRANSACTION_TYPE_LAYAWAY = TransactionType.LAYAWAY.value

KITCHEN_ORDER_STATUS_WAITING = KitchenOrderStatus.WAITING.value
KITCHEN_ORDER_STATUS_PREPARING = KitchenOrderStatus.PREPARING.value
KITCHEN_ORDER_STATUS_READY = KitchenOrderStatus.READY.value
KITCHEN_ORDER_STATUS_SERVED = KitchenOrderStatus.SERVED.value
KITCHEN_ORDER_STATUS_CANCELLED = KitchenOrderStatus.CANCELLED.value

DELIVERY_STATUS_PENDING = DeliveryStatus.PENDING.value
DELIVERY_STATUS_PREPARING = DeliveryStatus.PREPARING.value
DELIVERY_STATUS_READY = DeliveryStatus.READY.value
DELIVERY_STATUS_OUT_FOR_DELIVERY = DeliveryStatus.OUT_FOR_DELIVERY.value
DELIVERY_STATUS_DELIVERED = DeliveryStatus.DELIVERED.value
DELIVERY_STATUS_FAILED = DeliveryStatus.FAILED.value
DELIVERY_STATUS_RETURNED = DeliveryStatus.RETURNED.value 
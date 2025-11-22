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

# Data layer imports for external access
from data_layer.model import metadata
from data_layer.engine import Engine

# Model imports
from data_layer.model import Cashier
from data_layer.model import Customer
from data_layer.model import Store
from data_layer.model import Vat
from data_layer.model import ProductUnit
from data_layer.model import DepartmentMainGroup
from data_layer.model import DepartmentSubGroup
from data_layer.model import Product
from data_layer.model import ProductBarcode
from data_layer.model import ProductBarcodeMask
from data_layer.model import TransactionHead
from data_layer.model import TransactionHeadTemp
from data_layer.model import TransactionProduct
from data_layer.model import TransactionProductTemp
from data_layer.model import TransactionPayment
from data_layer.model import TransactionPaymentTemp
from data_layer.model import TransactionDepartment
from data_layer.model import TransactionDepartmentTemp
from data_layer.model import TransactionDiscount
from data_layer.model import TransactionDiscountTemp
from data_layer.model import Closure
from data_layer.model import ClosureCurrency

# Database management functions moved to db_manager.py
# Import example: from data_layer.db_manager import init_db, reset_db, check_db_connection
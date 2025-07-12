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

from data_layer.model.crud_model import CRUD, Model, metadata

from data_layer.model.definition.cashier import Cashier
from data_layer.model.definition.customer import Customer
from data_layer.model.definition.store import Store
from data_layer.model.definition.vat import Vat
from data_layer.model.definition.product_unit import ProductUnit
from data_layer.model.definition.department_main_group import DepartmentMainGroup
from data_layer.model.definition.department_sub_group import DepartmentSubGroup
from data_layer.model.definition.product import Product
from data_layer.model.definition.product_barcode import ProductBarcode
from data_layer.model.definition.product_barcode_mask import ProductBarcodeMask
from data_layer.model.definition.transaction_head import TransactionHead
from data_layer.model.definition.transaction_head_temp import TransactionHeadTemp
from data_layer.model.definition.transaction_product import TransactionProduct
from data_layer.model.definition.transaction_product_temp import TransactionProductTemp
from data_layer.model.definition.transaction_payment import TransactionPayment
from data_layer.model.definition.transaction_payment_temp import TransactionPaymentTemp
from data_layer.model.definition.transaction_total import TransactionTotal
from data_layer.model.definition.transaction_total_temp import TransactionTotalTemp
from data_layer.model.definition.transaction_discount import TransactionDiscount
from data_layer.model.definition.transaction_discount_temp import TransactionDiscountTemp
from data_layer.model.definition.closure import Closure
from data_layer.model.definition.closure_total import ClosureTotal
from data_layer.model.definition.closure_currency import ClosureCurrency
from data_layer.model.definition.closure_payment_type_summary import ClosurePaymentTypeSummary
from data_layer.model.definition.country import Country
from data_layer.model.definition.city import City
from data_layer.model.definition.district import District
from data_layer.model.definition.currency import Currency
from data_layer.model.definition.payment_type import PaymentType
from data_layer.model.definition.label_value import LabelValue
from data_layer.model.definition.pos_settings import PosSettings
from data_layer.model.definition.product_manufacturer import ProductManufacturer
from data_layer.model.definition.transaction_document_type import TransactionDocumentType
from data_layer.model.definition.transaction_sequence import TransactionSequence
from data_layer.model.definition.form import Form
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.receipt_header import ReceiptHeader
from data_layer.model.definition.receipt_footer import ReceiptFooter


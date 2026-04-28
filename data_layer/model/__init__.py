"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
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
from data_layer.model.definition.transaction_department import TransactionDepartment
from data_layer.model.definition.transaction_department_temp import TransactionDepartmentTemp
from data_layer.model.definition.transaction_discount import TransactionDiscount
from data_layer.model.definition.transaction_discount_temp import TransactionDiscountTemp
from data_layer.model.definition.transaction_discount_type import TransactionDiscountType
from data_layer.model.definition.closure import Closure
from data_layer.model.definition.closure_currency import ClosureCurrency
from data_layer.model.definition.closure_payment_type_summary import ClosurePaymentTypeSummary
from data_layer.model.definition.closure_cashier_summary import ClosureCashierSummary
from data_layer.model.definition.closure_department_summary import ClosureDepartmentSummary
from data_layer.model.definition.closure_discount_summary import ClosureDiscountSummary
from data_layer.model.definition.closure_document_type_summary import ClosureDocumentTypeSummary
from data_layer.model.definition.closure_tip_summary import ClosureTipSummary
from data_layer.model.definition.closure_vat_summary import ClosureVATSummary
from data_layer.model.definition.closure_country_specific import ClosureCountrySpecific
from data_layer.model.definition.country import Country
from data_layer.model.definition.country_region import CountryRegion
from data_layer.model.definition.city import City
from data_layer.model.definition.district import District
from data_layer.model.definition.currency import Currency
from data_layer.model.definition.currency_table import CurrencyTable
from data_layer.model.definition.payment_type import PaymentType
from data_layer.model.definition.label_value import LabelValue
from data_layer.model.definition.pos_settings import PosSettings
from data_layer.model.definition.product_manufacturer import ProductManufacturer
from data_layer.model.definition.transaction_document_type import TransactionDocumentType
from data_layer.model.definition.transaction_sequence import TransactionSequence
from data_layer.model.definition.form import Form
from data_layer.model.definition.form_control import FormControl
from data_layer.model.definition.form_control_tab import FormControlTab
from data_layer.model.definition.receipt_header import ReceiptHeader
from data_layer.model.definition.receipt_footer import ReceiptFooter
from data_layer.model.definition.table import Table
from data_layer.model.definition.transaction_delivery import TransactionDelivery
from data_layer.model.definition.transaction_delivery_temp import TransactionDeliveryTemp
from data_layer.model.definition.transaction_fiscal import TransactionFiscal
from data_layer.model.definition.transaction_fiscal_temp import TransactionFiscalTemp
from data_layer.model.definition.transaction_kitchen_order import TransactionKitchenOrder
from data_layer.model.definition.transaction_kitchen_order_temp import TransactionKitchenOrderTemp
from data_layer.model.definition.Transaction_loyalty import TransactionLoyalty
from data_layer.model.definition.transaction_loyalty_temp import TransactionLoyaltyTemp
from data_layer.model.definition.transaction_note import TransactionNote
from data_layer.model.definition.transaction_note_temp import TransactionNoteTemp
from data_layer.model.definition.transaction_refund import TransactionRefund
from data_layer.model.definition.transaction_refund_temp import TransactionRefundTemp
from data_layer.model.definition.transaction_surcharge import TransactionSurcharge
from data_layer.model.definition.transaction_surcharge_temp import TransactionSurchargeTemp
from data_layer.model.definition.transaction_tax import TransactionTax
from data_layer.model.definition.transaction_tax_temp import TransactionTaxTemp
from data_layer.model.definition.transaction_tip import TransactionTip
from data_layer.model.definition.transaction_tip_temp import TransactionTipTemp
from data_layer.model.definition.transaction_change import TransactionChange
from data_layer.model.definition.transaction_change_temp import TransactionChangeTemp
from data_layer.model.definition.transaction_status import TransactionStatus
from data_layer.model.definition.warehouse import Warehouse
from data_layer.model.definition.warehouse_location import WarehouseLocation
from data_layer.model.definition.warehouse_product_stock import WarehouseProductStock
from data_layer.model.definition.warehouse_stock_movement import WarehouseStockMovement
from data_layer.model.definition.warehouse_stock_adjustment import WarehouseStockAdjustment

# Product Models
from data_layer.model.definition.product_variant import ProductVariant
from data_layer.model.definition.product_attribute import ProductAttribute

# POS Settings Models
from data_layer.model.definition.pos_virtual_keyboard import PosVirtualKeyboard

# Cashier Performance Models
from data_layer.model.definition.cashier_work_session import CashierWorkSession
from data_layer.model.definition.cashier_performance_metrics import CashierPerformanceMetrics
from data_layer.model.definition.cashier_work_break import CashierWorkBreak
from data_layer.model.definition.cashier_performance_target import CashierPerformanceTarget
from data_layer.model.definition.cashier_transaction_metrics import CashierTransactionMetrics

# Campaign and Promotion Models
from data_layer.model.definition.campaign_type import CampaignType
from data_layer.model.definition.campaign import Campaign
from data_layer.model.definition.campaign_rule import CampaignRule
from data_layer.model.definition.campaign_product import CampaignProduct
from data_layer.model.definition.campaign_usage import CampaignUsage
from data_layer.model.definition.coupon import Coupon
from data_layer.model.definition.coupon_usage import CouponUsage

# Loyalty Program Models
from data_layer.model.definition.loyalty_program import LoyaltyProgram
from data_layer.model.definition.loyalty_tier import LoyaltyTier
from data_layer.model.definition.customer_loyalty import CustomerLoyalty
from data_layer.model.definition.loyalty_point_transaction import LoyaltyPointTransaction
from data_layer.model.definition.loyalty_program_policy import LoyaltyProgramPolicy
from data_layer.model.definition.loyalty_earn_rule import LoyaltyEarnRule
from data_layer.model.definition.loyalty_redemption_policy import LoyaltyRedemptionPolicy

# Customer Segmentation Models
from data_layer.model.definition.customer_segment import CustomerSegment
from data_layer.model.definition.customer_segment_member import CustomerSegmentMember

# Integration Layer Models
from data_layer.model.definition.sync_queue_item import SyncQueueItem
from data_layer.model.definition.gate_notification import GateNotification
from data_layer.model.definition.office_push_queue import OfficePushQueue
from data_layer.model.definition.office_closure_push_queue import OfficeClosurePushQueue


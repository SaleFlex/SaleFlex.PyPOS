# Event System

SaleFlex.PyPOS uses a **dictionary-based event dispatch** model. Every button click in the UI resolves to a string `EventName`, which `EventHandler.event_distributor()` maps to a Python callable. This document explains the flow end-to-end and catalogs all event categories.

---

## How a Button Click Becomes a Handler Call

```
User taps a button
        │
        ▼
BaseWindow (or DynamicDialog) reads button's
FormControl.form_control_function1  (e.g. "CASH_PAYMENT")
        │
        ▼
Interface.handle_event(event_name)
        │
        ▼
Application.event_distributor(event_name)
  ├─ Looks up event_name in event_handler_map dict
  └─ Returns the bound method (e.g. self._cash_payment_event)
        │
        ▼
handler()  ← called with zero or one argument (button widget)
```

The button widget is passed as the sole argument only for events in `quantity_events` and `payment_events` lists (defined in `BaseWindow`) — these handlers need to inspect the button name to determine amounts or modes.

---

## EventHandler Class

**File:** `pos/manager/event_handler.py`

`EventHandler` is assembled from ten mixin classes via multiple inheritance:

```python
class EventHandler(GeneralEvent, SaleEvent, PaymentEvent, ConfigurationEvent,
                   ServiceEvent, ReportEvent, HardwareEvent, WarehouseEvent,
                   ClosureEvent, ProductEvent):
```

It holds three pieces of state that span events:

| Attribute | Type | Initial | Purpose |
|-----------|------|---------|---------|
| `pending_quantity` | `float` | `1.0` | Quantity multiplier set by the X button; consumed by the next sale |
| `awaiting_plu_inquiry` | `bool` | `False` | When `True`, the next ENTER runs price/stock inquiry instead of selling |
| `key_pressed_count` / `key_value` | `int` / `str` | `0` / `""` | External keyboard buffering state |

### `event_distributor(event_name)`

Central router. Returns the handler callable for the given string, or `_not_defined_function` if not found.

```python
handler = app.event_distributor("LOGIN")
if handler:
    handler()
```

---

## Event Categories

### Application Lifecycle — `GeneralEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `EXIT_APPLICATION` | `_exit_application_event` | Close the application |
| `LOGIN` | `_login_event` | Authenticate from LOGIN form |
| `LOGIN_EXTENDED` | `_login_extended_event` | Extended login (service/supervisor) |
| `LOGOUT` | `_logout_event` | End current user session |
| `BACK` | `_back_event` | Navigate to previous form (history stack) |
| `CLOSE_FORM` | `_close_form_event` | Close a modal dialog |
| `SAVE_CHANGES` | `_save_changes_event` | Generic panel-based model save |
| `REDRAW_FORM` | `_redraw_form_event` | Redraw current form |

### Navigation — `GeneralEvent`

| EventName | Handler | Navigates to |
|-----------|---------|-------------|
| `SALE` / `SALES_FORM` | `_sales_form_event` | SALE screen |
| `CONFIG` / `SETTING_FORM` | `_settings_form_event` | SETTING screen |
| `CLOSURE` | `_closure_event` | Closure execution |
| `CLOSURE_FORM` | `_closure_form_event` | Closure form |
| `MAIN_MENU_FORM` | `_main_menu_form_event` | Main menu |
| `CASHIER` / `CASHIER_FORM` | `_cashier_form_event` | Cashier management |
| `SELECT_CASHIER` | `_select_cashier_event` | Combobox selection change |
| `ADD_NEW_CASHIER` | `_add_new_cashier_event` | Create blank cashier record |
| `CUSTOMER` / `CUSTOMER_FORM` | `_customer_form_event` | Customer form |
| `SERVICE_FORM` | `_service_form_event` | Service menu |
| `REPORT_FORM` | `_report_form_event` | Reports menu |

### Sales Operations — `SaleEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `SALE_PLU_BARCODE` | `_sale_plu_barcode_event` | NumPad ENTER — barcode/code lookup |
| `SALE_PLU_CODE` | `_sale_plu_code_event` | PLU button click |
| `SALE_DEPARTMENT` | `_sale_department_event` | Department button click |
| `SALE_DEPARTMENT_BY_NO` | `_sale_department_by_no_event` | Department by number |
| `INPUT_QUANTITY` | `_input_quantity_event` | X button — set quantity multiplier |
| `PLU_INQUIRY` | `_plu_inquiry_event` | PLU button — price and stock inquiry |
| `REPEAT_SALE` | `_repeat_sale_event` | Repeat selected line |
| `CANCEL_DOCUMENT` | `_cancel_document_event` | Void entire transaction (CANCEL button) |
| `CANCEL_SALE` | `_cancel_sale_event` | Cancel sale (alternate name) |
| `CANCEL_PLU` | `_cancel_plu_event` | Cancel last PLU line |
| `CANCEL_LAST_SALE` | `_cancel_last_sale_event` | Cancel last line |
| `SUSPEND_SALE` | `_suspend_sale_event` | Park current cart |
| `RESUME_SALE` | `_resume_sale_event` | Activate selected parked cart |
| `SUSPEND_LIST` | `_suspend_list_event` | Open suspended sales list |

### Payment Operations — `PaymentEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `PAYMENT` | `_payment_event` | Open **PAYMENT** form (full payment screen; SALE dual **CREDIT CARD** → **PAYMENT**) |
| `CASH_PAYMENT` | `_cash_payment_event` | Cash payment (exact or from NumPad) |
| `CREDIT_PAYMENT` | `_credit_payment_event` | Credit card payment |
| `CHECK_PAYMENT` | `_check_payment_event` | Cheque payment |
| `EXCHANGE_PAYMENT` | `_exchange_payment_event` | Foreign currency exchange |
| `PREPAID_PAYMENT` | `_prepaid_payment_event` | Prepaid card |
| `CHARGE_SALE_PAYMENT` | `_charge_sale_payment_event` | House charge / store credit |
| `OTHER_PAYMENT` | `_other_payment_event` | Unspecified payment method |
| `CHANGE_PAYMENT` | `_change_payment_event` | Record change given to customer |
| `PAYMENT_DETAIL` | `_payment_detail_event` | Show payment detail |

### Closure — `ClosureEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `CLOSURE` | `_closure_event` | Execute end-of-day closure |
| `CLOSURE_FORM` | `_closure_form_event` | Open closure form |
| `CLOSURE_DETAIL_FORM` | `_closure_detail_form_event` | Open closure detail form for the selected closure |
| `CLOSURE_RECEIPTS_FORM` | `_closure_receipts_form_event` | Open receipts list for the selected closure |
| `CLOSURE_RECEIPT_DETAIL_FORM` | `_closure_receipt_detail_form_event` | Open receipt detail for the selected receipt |

### Product Management — `ProductEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `PRODUCT_LIST_FORM` | `_product_list_form_event` | Open product list / search form |
| `PRODUCT_SEARCH` | `_product_search_event` | Execute search from textbox |
| `PRODUCT_DETAIL` | `_product_detail_event` | Open product detail dialog |

### Configuration — `ConfigurationEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `SET_CASHIER` | `_set_cashier_event` | Cashier definition |
| `SET_VAT_DEFINITION` | `_set_vat_definition_event` | VAT rate setup |
| `SET_DEPARTMENT_DEFINITION` | `_set_department_definition_event` | Department setup |
| `SET_PLU_DEFINITION` | `_set_plu_definition_event` | PLU/product setup |
| `SET_RECEIPT_HEADER` | `_set_receipt_header_event` | Receipt header text |
| `SET_RECEIPT_FOOTER` | `_set_receipt_footer_event` | Receipt footer text |
| `SET_CURRENCY_DEFINITION` | `_set_currency_definition_event` | Currency setup |
| `SET_DISCOUNT_RATE` | `_set_discount_rate_event` | Discount rate setup |
| `SET_DISPLAY_BRIGHTNESS` | `_set_display_brightness_event` | Screen brightness |

### Hardware — `HardwareEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `OPEN_CASH_DRAWER` | `_open_cash_drawer_event` | Open the cash drawer |

### Warehouse / Stock — `WarehouseEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `STOCK_IN` | `_stock_in_event` | Stock receipt |
| `STOCK_OUT` | `_stock_out_event` | Stock issue |
| `STOCK_TRANSFER` | `_stock_transfer_event` | Transfer between locations |
| `STOCK_ADJUSTMENT` | `_stock_adjustment_event` | Manual adjustment |
| `STOCK_COUNT` | `_stock_count_event` | Physical count |
| `WAREHOUSE_RECEIPT` | `_warehouse_receipt_event` | Warehouse goods receipt |
| `WAREHOUSE_ISSUE` | `_warehouse_issue_event` | Warehouse goods issue |

### Reports — `ReportEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `SALE_DETAIL_REPORT` | `_sale_detail_report_event` | Transaction detail report |
| `PLU_SALE_REPORT` | `_plu_sale_report_event` | Product sales report |
| `POS_SUMMARY_REPORT` | `_pos_summary_report_event` | POS summary |
| `INVOICE_LIST` | `_invoice_list_event` | Invoice list |
| `RETURN_LIST` | `_return_list_event` | Return/refund list |
| `STOCK_LIST` | `_stock_list_event` | Stock status list |

### Restaurant (Table/Check) — `SaleEvent`

| EventName | Handler | Description |
|-----------|---------|-------------|
| `TABLE_OPEN` | `_table_open_event` | Open a table |
| `TABLE_CLOSE` | `_table_close_event` | Close a table |
| `TABLE_SELECT` | `_table_select_event` | Select a table |
| `TABLE_TRANSFER` | `_table_transfer_event` | Transfer items to another table |
| `TABLE_MERGE` | `_table_merge_event` | Merge two tables |
| `ORDER_ADD` | `_order_add_event` | Add an order item |
| `ORDER_SEND_TO_KITCHEN` | `_order_send_to_kitchen_event` | Send order to kitchen display |
| `CHECK_PRINT` | `_check_print_event` | Print table check |
| `CHECK_SPLIT` | `_check_split_event` | Split check between guests |

---

## Adding a New Event

1. Add an entry to `EventName` enum in `data_layer/enums/event_name.py`.
2. Implement `_my_new_event(self)` in the most appropriate mixin (or create a new one).
3. Register it in `EventHandler.event_distributor()` → `event_handler_map`.
4. Set `form_control_function1 = "MY_NEW_EVENT"` on the `FormControl` database row that should trigger it.

---

[← Back to Table of Contents](README.md) | [Previous: UI Controls Catalog](23-ui-controls.md) | [Next: Service Layer →](25-service-layer.md)

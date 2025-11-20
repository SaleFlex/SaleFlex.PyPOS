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

from data_layer.enums import EventName
from pos.manager.event import (
    GeneralEvent, 
    SaleEvent, 
    PaymentEvent, 
    ConfigurationEvent, 
    ServiceEvent, 
    ReportEvent, 
    HardwareEvent,
    WarehouseEvent,
    ClosureEvent
)


class EventHandler(GeneralEvent, SaleEvent, PaymentEvent, ConfigurationEvent, 
                   ServiceEvent, ReportEvent, HardwareEvent, WarehouseEvent, ClosureEvent):
    """
    Central Event Processing Manager for SaleFlex Point of Sale System.
    
    This class serves as the main event dispatcher for the POS application,
    implementing multiple inheritance to combine specialized event handling
    capabilities from different domain-specific event handler classes.
    
    The class inherits from nine specialized event handler classes:
    - GeneralEvent: Handles basic application events (login, logout, exit, navigation)
    - SaleEvent: Processes sales transaction and product-related events
    - PaymentEvent: Manages all payment processing and payment methods
    - ConfigurationEvent: Handles system configuration and settings events
    - ServiceEvent: Manages service and maintenance operations
    - ReportEvent: Processes reporting and analytics events
    - HardwareEvent: Controls hardware operations and device communications
    - WarehouseEvent: Manages stock and warehouse inventory operations
    - ClosureEvent: Handles end-of-day closure and financial reconciliation operations
    
    The event distribution mechanism uses a dictionary-based approach to map
    event names to their corresponding handler functions, providing a
    centralized and organized approach to event processing with comprehensive
    error handling and fallback mechanisms.
    
    This class is designed to be inherited by the main Application class,
    providing comprehensive event handling capabilities throughout the application.
    """
    
    def __init__(self):
        """
        Initialize the EventHandler.
        
        Sets up any required state for event handling, including counters
        for external keyboard events and temporary storage for key values.
        """
        super().__init__()
        
        # External keyboard event handling state
        self.key_pressed_count = 0
        self.key_value = ""
    
    def event_distributor(self, event_name):
        """
        Central event distribution method that routes events to appropriate handlers.
        
        This method acts as a comprehensive dispatcher, taking an event name and returning the
        corresponding handler function without executing it. All event methods are now properly
        implemented in their respective event handler classes, eliminating the need for
        fallback mechanisms.
        
        The method maps all available events from the EventName enum to their respective
        handler functions, providing a complete event routing system for the POS application.
        
        Args:
            event_name (str): The name of the event to process, typically from EventName enum
            
        Returns:
            callable or None: The handler function for the specified event,
                            or a default handler if no specific handler is found,
                            or None if an error occurs during event distribution
                            
        Event Categories Handled:
            - Application Lifecycle: EXIT_APPLICATION, LOGIN, LOGOUT, etc.
            - Sales Operations: SALE_DEPARTMENT, SALE_PLU_CODE, etc.  
            - Payment Processing: CASH_PAYMENT, CREDIT_PAYMENT, etc.
            - System Configuration: SET_CASHIER, SET_RECEIPT_HEADER, etc.
            - Service Functions: SERVICE_COMPANY_INFO, SERVICE_RESET_PASSWORD, etc.
            - Reports: SALE_DETAIL_REPORT, PLU_SALE_REPORT, etc.
            - Hardware Control: OPEN_CASH_DRAWER, etc.
            - Restaurant Operations: TABLE_OPEN, ORDER_ADD, CHECK_PRINT, etc.
            - Sale Suspension: SUSPEND_SALE, RESUME_SALE, SUSPEND_LIST, etc.
            - Stock Operations: STOCK_IN, STOCK_OUT, STOCK_TRANSFER, etc.
            - Warehouse Operations: WAREHOUSE_RECEIPT, WAREHOUSE_ISSUE, etc.
            
        Example:
            handler = self.event_distributor("LOGIN")
            if handler:
                result = handler()  # Execute the login process
        """
        print(f"\n[EVENT_DISTRIBUTOR] Received event_name: '{event_name}' (type: {type(event_name)})")
        
        try:
            # Create a comprehensive dictionary mapping event names to handler functions
            # All methods are now properly implemented in their respective event classes
            event_handler_map = {
                # Basic/Core Events - From GeneralEvent
                EventName.NONE.name: self._none_function,
                EventName.EXIT_APPLICATION.name: self._exit_application,
                EventName.BACK.name: self._back,
                EventName.CLOSE_FORM.name: self._close_form,
                EventName.SAVE_CHANGES.name: self._save_changes,
                EventName.REDRAW_FORM.name: self._redraw_form,
                
                # Authentication Events - From GeneralEvent
                EventName.LOGIN.name: self._login,
                EventName.LOGIN_EXTENDED.name: self._login_extended,
                EventName.LOGOUT.name: self._logout,
                EventName.SERVICE_CODE_REQUEST.name: self._service_code_request,
                EventName.LOGIN_SERVICE.name: self._login_service,
                
                # Navigation Events - From GeneralEvent
                EventName.SALE.name: self._sales_form,
                EventName.SALES_FORM.name: self._sales_form,
                EventName.CONFIG.name: self._settings_form,
                EventName.SETTING_FORM.name: self._settings_form,
                EventName.CLOSURE.name: self._closure,
                EventName.CLOSURE_FORM.name: self._closure_form,
                EventName.MAIN_MENU_FORM.name: self._main_menu_form,
                EventName.SERVICE_FORM.name: self._service_form,
                EventName.REPORT_FORM.name: self._report_form,
                EventName.CASHIER_FORM.name: self._cashier_form,
                EventName.CASHIER.name: self._cashier_form,
                EventName.CUSTOMER_FORM.name: self._customer_form,
                EventName.CUSTOMER.name: self._customer_form,
                
                # Sales Events - From SaleEvent
                EventName.SALE_DEPARTMENT.name: self._sale_department,
                EventName.SALE_DEPARTMENT_BY_NO.name: self._sale_department_by_no,
                EventName.SALE_PLU_CODE.name: self._sale_plu_code,
                EventName.SALE_PLU_BARCODE.name: self._sale_plu_barcode,
                EventName.GET_PLU_FROM_MAINGROUP.name: self._get_plu_from_maingroup,
                EventName.REPEAT_LAST_SALE.name: self._repeat_last_sale,
                EventName.REPEAT_SALE.name: self._repeat_sale,
                EventName.SALE_OPTION.name: self._sale_option,
                EventName.SALE_SHORTCUT.name: self._sale_shortcut,
                
                # Cancellation Events - From SaleEvent
                EventName.CANCEL_DEPARTMENT.name: self._cancel_department,
                EventName.CANCEL_PLU.name: self._cancel_plu,
                EventName.CANCEL_LAST_SALE.name: self._cancel_last_sale,
                EventName.CANCEL_SALE.name: self._cancel_sale,
                EventName.CANCEL_DOCUMENT.name: self._cancel_document,
                
                # Transaction Modification Events - From SaleEvent
                EventName.CHANGE_DOCUMENT_TYPE.name: self._change_document_type,
                EventName.REFUND.name: self._refund,
                EventName.DISCOUNT_BY_AMOUNT.name: self._discount_by_amount,
                EventName.SURCHARGE_BY_AMOUNT.name: self._surcharge_by_amount,
                EventName.DISCOUNT_BY_PERCENT.name: self._discount_by_percent,
                EventName.SURCHARGE_BY_PERCENT.name: self._surcharge_by_percent,
                
                # Input Events - From SaleEvent
                EventName.INPUT_PRICE.name: self._input_price,
                EventName.INPUT_QUANTITY.name: self._input_quantity,
                EventName.INPUT_AMOUNT.name: self._input_amount,
                EventName.PRICE_LOOKUP.name: self._price_lookup,
                
                # Total and Subtotal Events - From SaleEvent
                EventName.SUBTOTAL.name: self._subtotal,
                EventName.TOTAL.name: self._total,
                EventName.CLEAR_BUFFER.name: self._clear_buffer,
                
                # Payment Events - From PaymentEvent
                EventName.PAYMENT.name: self._payment,
                EventName.CASH_PAYMENT.name: self._cash_payment,
                EventName.CREDIT_PAYMENT.name: self._credit_payment,
                EventName.CHECK_PAYMENT.name: self._check_payment,
                EventName.EXCHANGE_PAYMENT.name: self._exchange_payment,
                EventName.PREPAID_PAYMENT.name: self._prepaid_payment,
                EventName.CHARGE_SALE_PAYMENT.name: self._charge_sale_payment,
                EventName.OTHER_PAYMENT.name: self._other_payment,
                EventName.PAYMENT_DETAIL.name: self._payment_detail,
                EventName.SUSPEND_PAYMENT.name: self._suspend_payment,
                EventName.BACK_PAYMENT.name: self._back_payment,
                
                # Hardware Events - From HardwareEvent
                EventName.OPEN_CASH_DRAWER.name: self._open_cash_drawer,
                
                # Report Events - From ReportEvent
                EventName.SALE_DETAIL_REPORT.name: self._sale_detail_report,
                EventName.PLU_SALE_REPORT.name: self._plu_sale_report,
                EventName.POS_SUMMARY_REPORT.name: self._pos_summary_report,
                EventName.INVOICE_LIST.name: self._invoice_list,
                EventName.WAYBILL_LIST.name: self._waybill_list,
                EventName.RETURN_LIST.name: self._return_list,
                EventName.STOCK_LIST.name: self._stock_list,
                EventName.STOCK_ENTRY_FORM.name: self._stock_entry_form,
                
                # Configuration Events - From ConfigurationEvent
                EventName.SET_DISPLAY_BRIGHTNESS.name: self._set_display_brightness,
                EventName.SET_PRINTER_INTENSITY.name: self._set_printer_intensity,
                EventName.SET_CASHIER.name: self._set_cashier,
                EventName.SET_SUPERVISOR.name: self._set_supervisor,
                EventName.SET_RECEIPT_HEADER.name: self._set_receipt_header,
                EventName.SET_RECEIPT_FOOTER.name: self._set_receipt_footer,
                EventName.SET_IDLE_MESSAGE.name: self._set_idle_message,
                EventName.SET_BARCODE_DEFINITION.name: self._set_barcode_definition,
                EventName.SET_VAT_DEFINITION.name: self._set_vat_definition,
                EventName.SET_DEPARTMENT_DEFINITION.name: self._set_department_definition,
                EventName.SET_CURRENCY_DEFINITION.name: self._set_currency_definition,
                EventName.SET_PLU_DEFINITION.name: self._set_plu_definition,
                EventName.SET_PLU_MAINGROUP_DEFINITION.name: self._set_plu_maingroup_definition,
                EventName.SET_DISCOUNT_RATE.name: self._set_discount_rate,
                EventName.SET_SURCHARGE_RATE.name: self._set_surcharge_rate,
                
                # Service Events - From ServiceEvent
                EventName.SERVICE_COMPANY_INFO.name: self._service_company_info,
                EventName.SERVICE_CHANGE_DATE_TIME.name: self._service_change_date_time,
                EventName.SERVICE_PARAMETER_DOWNLOAD.name: self._service_parameter_download,
                EventName.SERVICE_SET_RECEIPT_LIMIT.name: self._service_set_receipt_limit,
                EventName.SERVICE_RESET_TO_FACTORY_MODE.name: self._service_reset_to_factory_mode,
                EventName.SERVICE_RESET_PASSWORD.name: self._service_reset_password,
                EventName.SERVICE_CHANGE_PASSWORD.name: self._service_change_password,
                EventName.SERVICE_POS_ACTIVE.name: self._service_pos_active,
                EventName.SERVICE_SOFTWARE_DOWNLOAD.name: self._service_software_download,
                EventName.SERVICE_GET_PLU_LIST.name: self._service_get_plu_list,
                
                # Restaurant Table Events - From SaleEvent
                EventName.TABLE_OPEN.name: self._table_open,
                EventName.TABLE_CLOSE.name: self._table_close,
                EventName.TABLE_SELECT.name: self._table_select,
                EventName.TABLE_TRANSFER.name: self._table_transfer,
                EventName.TABLE_MERGE.name: self._table_merge,
                EventName.TABLE_SPLIT.name: self._table_split,
                EventName.TABLE_STATUS.name: self._table_status,
                EventName.TABLE_LIST.name: self._table_list,
                
                # Restaurant Order Events - From SaleEvent
                EventName.ORDER_ADD.name: self._order_add,
                EventName.ORDER_CANCEL.name: self._order_cancel,
                EventName.ORDER_MODIFY.name: self._order_modify,
                EventName.ORDER_SEND_TO_KITCHEN.name: self._order_send_to_kitchen,
                EventName.ORDER_READY.name: self._order_ready,
                
                # Restaurant Check Events - From SaleEvent
                EventName.CHECK_OPEN.name: self._check_open,
                EventName.CHECK_CLOSE.name: self._check_close,
                EventName.CHECK_PRINT.name: self._check_print,
                EventName.CHECK_SPLIT.name: self._check_split,
                EventName.CHECK_MERGE.name: self._check_merge,
                
                # Market Sale Suspension Events - From SaleEvent
                EventName.SUSPEND_SALE.name: self._suspend_sale,
                EventName.RESUME_SALE.name: self._resume_sale,
                EventName.SUSPEND_LIST.name: self._suspend_list,
                EventName.DELETE_SUSPENDED_SALE.name: self._delete_suspended_sale,
                EventName.SUSPEND_DETAIL.name: self._suspend_detail,
                
                # Stock Events - From WarehouseEvent
                EventName.STOCK_IN.name: self._stock_in,
                EventName.STOCK_OUT.name: self._stock_out,
                EventName.STOCK_TRANSFER.name: self._stock_transfer,
                EventName.STOCK_ADJUSTMENT.name: self._stock_adjustment,
                EventName.STOCK_COUNT.name: self._stock_count,
                EventName.STOCK_MOVEMENT.name: self._stock_movement,
                EventName.STOCK_INQUIRY.name: self._stock_inquiry,
                
                # Warehouse Events - From WarehouseEvent
                EventName.WAREHOUSE_RECEIPT.name: self._warehouse_receipt,
                EventName.WAREHOUSE_ISSUE.name: self._warehouse_issue,
                EventName.WAREHOUSE_TRANSFER.name: self._warehouse_transfer,
                EventName.WAREHOUSE_ADJUSTMENT.name: self._warehouse_adjustment,
                EventName.WAREHOUSE_COUNT.name: self._warehouse_count,
                EventName.WAREHOUSE_LOCATION.name: self._warehouse_location,
            }
            
            # Try to find the event handler in the dictionary
            if event_name in event_handler_map:
                handler = event_handler_map[event_name]
                print(f"[EVENT_DISTRIBUTOR] ✓ Found handler for '{event_name}': {handler}")
                return handler
            
            # Return the default handler if no matching event handler is found
            print(f"[EVENT_DISTRIBUTOR] ✗ No handler found for '{event_name}', returning default handler")
            print(f"[EVENT_DISTRIBUTOR] Available keys sample: {list(event_handler_map.keys())[:10]}")
            return self._not_defined_function
            
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error in event_distributor for event '{event_name}': {str(e)}")
            # Return None in case of any error during event handler assignment
            return None
    
    def _not_defined_function(self):
        """
        Default handler for undefined or unimplemented events.
        
        This method serves as a fallback when an event is requested but
        no specific handler is implemented for it. It can be used for
        logging unhandled events or providing default behavior.
        
        Returns:
            bool: False to indicate the event was not processed
        """
        print("Event handler not defined - using default handler")
        return False
    
    def _none_function(self):
        """
        Handler for NONE events.
        
        This method handles the NONE event type, which represents
        no operation or placeholder events.
        
        Returns:
            bool: True to indicate successful handling of none operation
        """
        # Explicitly do nothing for NONE events
        return True

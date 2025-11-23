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
                EventName.NONE.name: self._none_function_event,
                EventName.EXIT_APPLICATION.name: self._exit_application_event,
                EventName.BACK.name: self._back_event,
                EventName.CLOSE_FORM.name: self._close_form_event,
                EventName.SAVE_CHANGES.name: self._save_changes_event,
                EventName.REDRAW_FORM.name: self._redraw_form_event,
                
                # Authentication Events - From GeneralEvent
                EventName.LOGIN.name: self._login_event,
                EventName.LOGIN_EXTENDED.name: self._login_extended_event,
                EventName.LOGOUT.name: self._logout_event,
                EventName.SERVICE_CODE_REQUEST.name: self._service_code_request_event,
                EventName.LOGIN_SERVICE.name: self._login_service_event,
                
                # Navigation Events - From GeneralEvent
                EventName.SALE.name: self._sales_form_event,
                EventName.SALES_FORM.name: self._sales_form_event,
                EventName.CONFIG.name: self._settings_form_event,
                EventName.SETTING_FORM.name: self._settings_form_event,
                EventName.CLOSURE.name: self._closure_event,
                EventName.CLOSURE_FORM.name: self._closure_form_event,
                EventName.MAIN_MENU_FORM.name: self._main_menu_form_event,
                EventName.SERVICE_FORM.name: self._service_form_event,
                EventName.REPORT_FORM.name: self._report_form_event,
                EventName.CASHIER_FORM.name: self._cashier_form_event,
                EventName.CASHIER.name: self._cashier_form_event,
                EventName.CUSTOMER_FORM.name: self._customer_form_event,
                EventName.CUSTOMER.name: self._customer_form_event,
                
                # Sales Events - From SaleEvent
                EventName.SALE_DEPARTMENT.name: self._sale_department_event,
                EventName.SALE_DEPARTMENT_BY_NO.name: self._sale_department_by_no_event,
                EventName.SALE_PLU_CODE.name: self._sale_plu_code_event,
                EventName.SALE_PLU_BARCODE.name: self._sale_plu_barcode_event,
                EventName.GET_PLU_FROM_MAINGROUP.name: self._get_plu_from_maingroup_event,
                EventName.REPEAT_LAST_SALE.name: self._repeat_last_sale_event,
                EventName.REPEAT_SALE.name: self._repeat_sale_event,
                EventName.SALE_OPTION.name: self._sale_option_event,
                EventName.SALE_SHORTCUT.name: self._sale_shortcut_event,
                
                # Cancellation Events - From SaleEvent
                EventName.CANCEL_DEPARTMENT.name: self._cancel_department_event,
                EventName.CANCEL_PLU.name: self._cancel_plu_event,
                EventName.CANCEL_LAST_SALE.name: self._cancel_last_sale_event,
                EventName.CANCEL_SALE.name: self._cancel_sale_event,
                EventName.CANCEL_DOCUMENT.name: self._cancel_document_event,
                
                # Transaction Modification Events - From SaleEvent
                EventName.CHANGE_DOCUMENT_TYPE.name: self._change_document_type_event,
                EventName.REFUND.name: self._refund_event,
                EventName.DISCOUNT_BY_AMOUNT.name: self._discount_by_amount_event,
                EventName.SURCHARGE_BY_AMOUNT.name: self._surcharge_by_amount_event,
                EventName.DISCOUNT_BY_PERCENT.name: self._discount_by_percent_event,
                EventName.SURCHARGE_BY_PERCENT.name: self._surcharge_by_percent_event,
                
                # Input Events - From SaleEvent
                EventName.INPUT_PRICE.name: self._input_price_event,
                EventName.INPUT_QUANTITY.name: self._input_quantity_event,
                EventName.INPUT_AMOUNT.name: self._input_amount_event,
                EventName.PRICE_LOOKUP.name: self._price_lookup_event,
                
                # Total and Subtotal Events - From SaleEvent
                EventName.SUBTOTAL.name: self._subtotal_event,
                EventName.TOTAL.name: self._total_event,
                EventName.CLEAR_BUFFER.name: self._clear_buffer_event,
                
                # Payment Events - From PaymentEvent
                EventName.PAYMENT.name: self._payment_event,
                EventName.CASH_PAYMENT.name: self._cash_payment_event,
                EventName.CREDIT_PAYMENT.name: self._credit_payment_event,
                EventName.CHECK_PAYMENT.name: self._check_payment_event,
                EventName.EXCHANGE_PAYMENT.name: self._exchange_payment_event,
                EventName.PREPAID_PAYMENT.name: self._prepaid_payment_event,
                EventName.CHARGE_SALE_PAYMENT.name: self._charge_sale_payment_event,
                EventName.OTHER_PAYMENT.name: self._other_payment_event,
                EventName.CHANGE_PAYMENT.name: self._change_payment_event,
                EventName.PAYMENT_DETAIL.name: self._payment_detail_event,
                EventName.SUSPEND_PAYMENT.name: self._suspend_payment_event,
                EventName.BACK_PAYMENT.name: self._back_payment_event,
                
                # Hardware Events - From HardwareEvent
                EventName.OPEN_CASH_DRAWER.name: self._open_cash_drawer_event,
                
                # Report Events - From ReportEvent
                EventName.SALE_DETAIL_REPORT.name: self._sale_detail_report_event,
                EventName.PLU_SALE_REPORT.name: self._plu_sale_report_event,
                EventName.POS_SUMMARY_REPORT.name: self._pos_summary_report_event,
                EventName.INVOICE_LIST.name: self._invoice_list_event,
                EventName.WAYBILL_LIST.name: self._waybill_list_event,
                EventName.RETURN_LIST.name: self._return_list_event,
                EventName.STOCK_LIST.name: self._stock_list_event,
                EventName.STOCK_ENTRY_FORM.name: self._stock_entry_form_event,
                
                # Configuration Events - From ConfigurationEvent
                EventName.SET_DISPLAY_BRIGHTNESS.name: self._set_display_brightness_event,
                EventName.SET_PRINTER_INTENSITY.name: self._set_printer_intensity_event,
                EventName.SET_CASHIER.name: self._set_cashier_event,
                EventName.SET_SUPERVISOR.name: self._set_supervisor_event,
                EventName.SET_RECEIPT_HEADER.name: self._set_receipt_header_event,
                EventName.SET_RECEIPT_FOOTER.name: self._set_receipt_footer_event,
                EventName.SET_IDLE_MESSAGE.name: self._set_idle_message_event,
                EventName.SET_BARCODE_DEFINITION.name: self._set_barcode_definition_event,
                EventName.SET_VAT_DEFINITION.name: self._set_vat_definition_event,
                EventName.SET_DEPARTMENT_DEFINITION.name: self._set_department_definition_event,
                EventName.SET_CURRENCY_DEFINITION.name: self._set_currency_definition_event,
                EventName.SET_PLU_DEFINITION.name: self._set_plu_definition_event,
                EventName.SET_PLU_MAINGROUP_DEFINITION.name: self._set_plu_maingroup_definition_event,
                EventName.SET_DISCOUNT_RATE.name: self._set_discount_rate_event,
                EventName.SET_SURCHARGE_RATE.name: self._set_surcharge_rate_event,
                
                # Service Events - From ServiceEvent
                EventName.SERVICE_COMPANY_INFO.name: self._service_company_info_event,
                EventName.SERVICE_CHANGE_DATE_TIME.name: self._service_change_date_time_event,
                EventName.SERVICE_PARAMETER_DOWNLOAD.name: self._service_parameter_download_event,
                EventName.SERVICE_SET_RECEIPT_LIMIT.name: self._service_set_receipt_limit_event,
                EventName.SERVICE_RESET_TO_FACTORY_MODE.name: self._service_reset_to_factory_mode_event,
                EventName.SERVICE_RESET_PASSWORD.name: self._service_reset_password_event,
                EventName.SERVICE_CHANGE_PASSWORD.name: self._service_change_password_event,
                EventName.SERVICE_POS_ACTIVE.name: self._service_pos_active_event,
                EventName.SERVICE_SOFTWARE_DOWNLOAD.name: self._service_software_download_event,
                EventName.SERVICE_GET_PLU_LIST.name: self._service_get_plu_list_event,
                
                # Restaurant Table Events - From SaleEvent
                EventName.TABLE_OPEN.name: self._table_open_event,
                EventName.TABLE_CLOSE.name: self._table_close_event,
                EventName.TABLE_SELECT.name: self._table_select_event,
                EventName.TABLE_TRANSFER.name: self._table_transfer_event,
                EventName.TABLE_MERGE.name: self._table_merge_event,
                EventName.TABLE_SPLIT.name: self._table_split_event,
                EventName.TABLE_STATUS.name: self._table_status_event,
                EventName.TABLE_LIST.name: self._table_list_event,
                
                # Restaurant Order Events - From SaleEvent
                EventName.ORDER_ADD.name: self._order_add_event,
                EventName.ORDER_CANCEL.name: self._order_cancel_event,
                EventName.ORDER_MODIFY.name: self._order_modify_event,
                EventName.ORDER_SEND_TO_KITCHEN.name: self._order_send_to_kitchen_event,
                EventName.ORDER_READY.name: self._order_ready_event,
                
                # Restaurant Check Events - From SaleEvent
                EventName.CHECK_OPEN.name: self._check_open_event,
                EventName.CHECK_CLOSE.name: self._check_close_event,
                EventName.CHECK_PRINT.name: self._check_print_event,
                EventName.CHECK_SPLIT.name: self._check_split_event,
                EventName.CHECK_MERGE.name: self._check_merge_event,
                
                # Market Sale Suspension Events - From SaleEvent
                EventName.SUSPEND_SALE.name: self._suspend_sale_event,
                EventName.RESUME_SALE.name: self._resume_sale_event,
                EventName.SUSPEND_LIST.name: self._suspend_list_event,
                EventName.DELETE_SUSPENDED_SALE.name: self._delete_suspended_sale_event,
                EventName.SUSPEND_DETAIL.name: self._suspend_detail_event,
                
                # Stock Events - From WarehouseEvent
                EventName.STOCK_IN.name: self._stock_in_event,
                EventName.STOCK_OUT.name: self._stock_out_event,
                EventName.STOCK_TRANSFER.name: self._stock_transfer_event,
                EventName.STOCK_ADJUSTMENT.name: self._stock_adjustment_event,
                EventName.STOCK_COUNT.name: self._stock_count_event,
                EventName.STOCK_MOVEMENT.name: self._stock_movement_event,
                EventName.STOCK_INQUIRY.name: self._stock_inquiry_event,
                
                # Warehouse Events - From WarehouseEvent
                EventName.WAREHOUSE_RECEIPT.name: self._warehouse_receipt_event,
                EventName.WAREHOUSE_ISSUE.name: self._warehouse_issue_event,
                EventName.WAREHOUSE_TRANSFER.name: self._warehouse_transfer_event,
                EventName.WAREHOUSE_ADJUSTMENT.name: self._warehouse_adjustment_event,
                EventName.WAREHOUSE_COUNT.name: self._warehouse_count_event,
                EventName.WAREHOUSE_LOCATION.name: self._warehouse_location_event,
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
    
    def _none_function_event(self):
        """
        Handler for NONE events.
        
        This method handles the NONE event type, which represents
        no operation or placeholder events.
        
        Returns:
            bool: True to indicate successful handling of none operation
        """
        # Explicitly do nothing for NONE events
        return True

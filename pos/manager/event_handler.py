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

from data_layer.enums import EventName
from pos.manager.event import (
    GeneralEvent, 
    SaleEvent, 
    PaymentEvent, 
    ConfigurationEvent, 
    ServiceEvent, 
    ReportEvent, 
    HardwareEvent
)


class EventHandler(GeneralEvent, SaleEvent, PaymentEvent, ConfigurationEvent, 
                   ServiceEvent, ReportEvent, HardwareEvent):
    """
    Central Event Processing Manager for SaleFlex Point of Sale System.
    
    This class serves as the main event dispatcher for the POS application,
    implementing multiple inheritance to combine specialized event handling
    capabilities from different domain-specific event handler classes.
    
    The class inherits from seven specialized event handler classes:
    - GeneralEvent: Handles basic application events (login, logout, exit, navigation)
    - SaleEvent: Processes sales transaction and product-related events
    - PaymentEvent: Manages all payment processing and payment methods
    - ConfigurationEvent: Handles system configuration and settings events
    - ServiceEvent: Manages service and maintenance operations
    - ReportEvent: Processes reporting and analytics events
    - HardwareEvent: Controls hardware operations and device communications
    
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
            
        Example:
            handler = self.event_distributor("LOGIN")
            if handler:
                result = handler()  # Execute the login process
        """
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
                EventName.SALE.name: self._sale,
                EventName.CONFIG.name: self._configuration,
                EventName.CLOSURE.name: self._closure,
                EventName.FUNCTION_MENU.name: self._function_menu,
                EventName.SALES_MENU.name: self._sales_menu,
                EventName.SERVICE_MENU.name: self._service_menu,
                EventName.SETTING_MENU.name: self._setting_menu,
                EventName.REPORT_MENU.name: self._report_menu,
                EventName.CASHIER.name: self._cashier,
                EventName.CUSTOMER.name: self._customer,
                
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
            }
            
            # Try to find the event handler in the dictionary
            if event_name in event_handler_map:
                return event_handler_map[event_name]
            
            # Return the default handler if no matching event handler is found
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

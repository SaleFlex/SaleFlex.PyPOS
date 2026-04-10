"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

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

import os
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt

from core.logger import get_logger

logger = get_logger(__name__)
from PySide6.QtGui import QIcon, QColor, QLinearGradient, QBrush, QPalette

from user_interface.control import TextBox, CheckBox, Button, NumPad, PaymentList, SaleList, ComboBox, AmountTable, Label, DataGrid, Panel, TabControl
from user_interface.control import VirtualKeyboard


class DynamicDialog(QDialog):
    """
    Dynamic modal dialog that renders forms from database definitions.
    
    This class creates modal dialogs that display forms defined in the database,
    using the same rendering logic as BaseWindow but in a modal context.
    """
    
    def __init__(self, app, parent=None):
        """
        Initialize the dynamic dialog.
        
        Args:
            app: The main application instance
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.app = app
        self.keyboard = VirtualKeyboard(source=None, parent=self)
        # Explicitly hide so Qt's showChildren does not auto-show the keyboard
        # when the dialog is displayed (it would resize to 970×315 and block events).
        self.keyboard.hide()
        self.payment_list = None
        self.sale_list = None
        self.amount_table = None
        self._panels = {}
        self._tab_controls = {}
        self._tab_pages = {}   # str(tab_id) → QWidget (tab page)
        self._dual_function_buttons = []
        self._func_mode_active = False
        
        # Make dialog modal and frameless
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Set window icon from settings
        self._set_window_icon()
    
    def _set_window_icon(self):
        """Set the window icon from settings.toml configuration."""
        try:
            from settings.settings import Settings
            icon_path = Settings().app_icon
            if icon_path and os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass  # Silently fail if icon cannot be loaded

    def _reset_all_dual_buttons_to_primary(self):
        """After any dual-function action, return every dual button to state 1 (caption1)."""
        self._func_mode_active = False
        for btn in self._dual_function_buttons:
            btn.reset_to_primary_state()

    def draw_window(self, settings: dict, toolbar_settings: dict, design: list):
        """
        Draw the dialog content based on design specifications.
        
        Args:
            settings (dict): Form settings (size, colors, etc.)
            toolbar_settings (dict): Toolbar configuration (not used in dialogs)
            design (list): List of control designs to render
        """
        self.setUpdatesEnabled(False)
        
        self.setWindowTitle(settings["name"])
        self.setFixedSize(settings["width"], settings["height"])
        self._apply_gradient_background(
            settings.get('background_color', 0xFFFFFF),
            settings.get('foreground_color', 0x000000)
        )
        
        # Reset panel / tab dictionaries for this draw pass
        if not hasattr(self, '_panels'):
            self._panels = {}
        else:
            self._panels.clear()
        if not hasattr(self, '_tab_controls'):
            self._tab_controls = {}
        else:
            self._tab_controls.clear()
        if not hasattr(self, '_tab_pages'):
            self._tab_pages = {}
        else:
            self._tab_pages.clear()
        self._dual_function_buttons = []
        self._func_mode_active = False

        # Render all controls
        for control_design_data in design:
            control_type = control_design_data["type"]

            if control_type == "textbox":
                self._create_textbox(control_design_data)
            elif control_type == "checkbox":
                self._create_checkbox(control_design_data)
            elif control_type == "button":
                self._create_button(control_design_data)
            elif control_type == "label":
                self._create_label(control_design_data)
            elif control_type == "numpad":
                self._create_numpad(control_design_data)
            elif control_type == "paymentlist":
                self._create_payment_list(control_design_data)
            elif control_type == "saleslist":
                self._create_sale_list(control_design_data)
            elif control_type == "amountstable":
                self._create_amount_table(control_design_data)
            elif control_type == "combobox":
                self._create_combobox(control_design_data)
            elif control_type == "datagrid":
                self._create_datagrid(control_design_data)
            elif control_type == "panel":
                self._create_panel(control_design_data)
            elif control_type == "tabcontrol":
                self._create_tab_control(control_design_data)
        
        self.setUpdatesEnabled(True)
        
        # Update keyboard size and position
        self.keyboard.resize_from_parent()
        self.keyboard.raise_()
    
    def _apply_gradient_background(self, background_value: int, foreground_value: int):
        """
        Apply a subtle gradient to match BaseWindow styling.
        """
        base_color = self._int_to_qcolor(background_value, default=QColor(255, 255, 255))
        dark_color = base_color.darker(120)
        light_color = base_color.lighter(120)

        gradient = QLinearGradient(0, 0, 0, self.height() or 1)
        gradient.setColorAt(0.0, dark_color)
        gradient.setColorAt(0.5, base_color)
        gradient.setColorAt(1.0, light_color)

        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        palette.setColor(QPalette.WindowText, self._int_to_qcolor(foreground_value, default=QColor(0, 0, 0)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    @staticmethod
    def _int_to_qcolor(value, default: QColor):
        """Safely convert an integer RGB value to QColor."""
        try:
            rgb = int(value)
        except (TypeError, ValueError):
            return default

        rgb = max(0, min(0xFFFFFF, rgb))
        r = (rgb >> 16) & 0xFF
        g = (rgb >> 8) & 0xFF
        b = rgb & 0xFF
        return QColor(r, g, b)
    
    def focus_text_box(self):
        """Set focus to the first textbox found."""
        for item in self.children():
            if type(item) is TextBox:
                item.setFocus()
                break
    
    def get_textbox_values(self):
        """
        Get all textbox values.
        
        Returns:
            dict: Dictionary of field_name -> value pairs
        """
        values = {}
        for item in self.children():
            if type(item) is TextBox:
                values[item.__name__] = item.text()
        return values
    
    def get_panel_textbox_values(self, panel_name):
        """
        Get all textbox values from a specific panel.
        
        Args:
            panel_name (str): Name of the panel (e.g., "POS_SETTINGS")
            
        Returns:
            dict: Dictionary mapping field names (lowercase) to textbox values
        """
        values = {}
        try:
            if not hasattr(self, '_panels'):
                return values
            
            panel = self._panels.get(panel_name)
            if not panel:
                return values
            
            try:
                if not hasattr(panel, 'get_content_widget'):
                    return values
            except RuntimeError:
                logger.warning("[GET_PANEL_VALUES] Panel '%s' widget already deleted", panel_name)
                return values
            
            try:
                content_widget = panel.get_content_widget()
                if not content_widget:
                    return values
                
                try:
                    _ = content_widget.children()
                except RuntimeError:
                    logger.warning("[GET_PANEL_VALUES] Content widget for panel '%s' already deleted", panel_name)
                    return values
                
                for child in content_widget.findChildren(TextBox):
                    try:
                        _ = child.text()
                    except RuntimeError:
                        continue
                    
                    textbox_name = getattr(child, 'name', None) or getattr(child, '__name__', None)
                    if textbox_name:
                        field_name = textbox_name.lower()
                        values[field_name] = child.text()
                
                for child in content_widget.findChildren(CheckBox):
                    try:
                        _ = child.isChecked()
                    except RuntimeError:
                        continue
                    cb_name = getattr(child, 'name', None) or getattr(child, '__name__', None)
                    if cb_name:
                        field_name = cb_name.lower()
                        values[field_name] = "true" if child.isChecked() else "false"
            except RuntimeError as e:
                logger.warning("[GET_PANEL_VALUES] Error accessing panel '%s': %s", panel_name, e)
                return values
            except Exception as e:
                logger.warning("[GET_PANEL_VALUES] Unexpected error accessing panel '%s': %s", panel_name, e)
                return values
        
        except Exception as e:
            logger.warning("[GET_PANEL_VALUES] Error getting panel values for '%s': %s", panel_name, e)
            return values
        
        return values

    def clear(self):
        """Clear and cleanup all child widgets."""
        if hasattr(self, '_tab_pages'):
            self._tab_pages.clear()
        if hasattr(self, '_tab_controls'):
            self._tab_controls.clear()
        for item in self.children():
            if type(item) in [TextBox, CheckBox, Button, Label, NumPad, PaymentList,
                               SaleList, ComboBox, AmountTable, DataGrid, Panel, TabControl]:
                item.deleteLater()
                item.setParent(None)
    
    # ------------------------------------------------------------------ #
    # Tab control                                                         #
    # ------------------------------------------------------------------ #

    def _create_tab_control(self, design_data):
        """
        Create a TabControl widget and populate its tab pages from DB definitions.

        Tab page ``QWidget`` instances are stored in ``self._tab_pages`` keyed by
        their ``form_control_tab.id`` (string) so that child controls created in
        subsequent ``_create_*`` calls can look up the correct parent widget.

        Each tab page gets a ``QVBoxLayout`` so child DataGrids fill it
        automatically instead of needing explicit geometry.

        Args:
            design_data (dict): Must contain a ``tabs`` list as produced by
                                ``DynamicFormRenderer._load_tabs_for_control``.
        """
        from PySide6.QtWidgets import QWidget, QVBoxLayout

        width = design_data.get("width", 900)
        height = design_data.get("height", 500)
        background_color = design_data.get("background_color", 0x2F4F4F)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        font_size = int(design_data.get("font_size", 12))

        tab_ctrl = TabControl(
            self,
            width=width,
            height=height,
            location_x=design_data.get("location_x", 0),
            location_y=design_data.get("location_y", 0),
            background_color=background_color,
            foreground_color=foreground_color,
            font_size=font_size,
        )

        ctrl_name = design_data.get("name", "")
        if ctrl_name:
            tab_ctrl.name = ctrl_name
            self._tab_controls[ctrl_name] = tab_ctrl

        for tab_info in sorted(design_data.get("tabs", []), key=lambda t: t["tab_index"]):
            page = QWidget()
            page.setObjectName(f"tab_page_{tab_info['tab_index']}")
            # Use a layout so the child DataGrid stretches to fill the page
            layout = QVBoxLayout(page)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(0)
            tab_ctrl.add_tab(page, tab_info["tab_title"])
            if tab_info.get("id"):
                self._tab_pages[tab_info["id"]] = page

        tab_ctrl.show()

    # ------------------------------------------------------------------ #
    # Product-detail grid helpers                                         #
    # ------------------------------------------------------------------ #

    def _get_current_product(self):
        """Return the Product for ``self.app.current_product_id``, or None."""
        product_id = getattr(self.app, "current_product_id", None)
        if not product_id:
            logger.warning("[PRODUCT_DETAIL] current_product_id is not set on app")
            return None
        try:
            from uuid import UUID as _UUID
            from data_layer.model import Product
            # SQLAlchemy's UUID column type requires a uuid.UUID object (not a plain
            # string) when filtering, otherwise it fails with 'str has no .hex'.
            if isinstance(product_id, str):
                product_id = _UUID(product_id)
            product = Product.get_by_id(product_id)
            if not product:
                logger.warning("[PRODUCT_DETAIL] Product not found for id: %s", product_id)
            return product
        except Exception as exc:
            logger.exception("[PRODUCT_DETAIL] Error loading product: %s", exc)
            return None

    def _populate_product_info_grid(self, datagrid):
        """Fill the Product-Info tab grid with key/value rows."""
        product = self._get_current_product()
        datagrid.set_columns(["Field", "Value"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductUnit, ProductManufacturer

            from uuid import UUID as _UUID

            def _to_uuid(val):
                if val is None:
                    return None
                return _UUID(str(val)) if not isinstance(val, _UUID) else val

            unit = None
            if getattr(product, "fk_product_unit_id", None):
                unit = ProductUnit.get_by_id(_to_uuid(product.fk_product_unit_id))

            # The FK column on Product is fk_manufacturer_id (not fk_product_manufacturer_id)
            mfr = None
            if getattr(product, "fk_manufacturer_id", None):
                mfr = ProductManufacturer.get_by_id(_to_uuid(product.fk_manufacturer_id))

            def _fmt(val):
                if val is None:
                    return ""
                try:
                    return f"{float(val):.2f}"
                except (TypeError, ValueError):
                    return str(val)

            rows = [
                ["Code",           product.code or ""],
                ["Name",           product.name or ""],
                ["Short Name",     product.short_name or ""],
                ["Sale Price",     _fmt(product.sale_price)],
                ["Purchase Price", _fmt(product.purchase_price)],
                ["Stock",          str(product.stock) if product.stock is not None else ""],
                ["Min Stock",      str(product.min_stock) if product.min_stock is not None else ""],
                ["Max Stock",      str(product.max_stock) if product.max_stock is not None else ""],
                ["Unit",           unit.name if unit else ""],
                ["Manufacturer",   mfr.name if mfr else ""],
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_INFO_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _populate_product_barcode_grid(self, datagrid):
        """Fill the Barcodes tab grid."""
        product = self._get_current_product()
        datagrid.set_columns(["Barcode", "Old Barcode", "Purchase Price", "Sale Price"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductBarcode
            barcodes = [b for b in ProductBarcode.get_all(is_deleted=False)
                        if str(b.fk_product_id) == str(product.id)]
            rows = [
                [
                    b.barcode or "",
                    b.old_barcode or "",
                    f"{float(b.purchase_price):.2f}" if b.purchase_price else "",
                    f"{float(b.sale_price):.2f}" if b.sale_price else "",
                ]
                for b in barcodes
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_BARCODE_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _populate_product_attribute_grid(self, datagrid):
        """Fill the Attributes tab grid."""
        product = self._get_current_product()
        datagrid.set_columns(["Attribute", "Value", "Category", "Unit"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductAttribute
            attrs = [a for a in ProductAttribute.get_all(is_deleted=False)
                     if str(a.fk_product_id) == str(product.id)]
            attrs.sort(key=lambda a: (a.display_order or 0, a.attribute_name or ""))
            rows = [
                [
                    a.display_name or a.attribute_name or "",
                    a.attribute_value or "",
                    a.category or "",
                    a.unit or "",
                ]
                for a in attrs
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_ATTRIBUTE_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _populate_product_variant_grid(self, datagrid):
        """Fill the Variants tab grid."""
        product = self._get_current_product()
        datagrid.set_columns(["Name", "Code", "Color", "Size", "Additional Info"])
        if not product:
            datagrid.set_data([])
            return
        try:
            from data_layer.model import ProductVariant
            variants = [v for v in ProductVariant.get_all(is_deleted=False)
                        if str(v.fk_product_id) == str(product.id)]
            rows = [
                [
                    v.variant_name or "",
                    v.variant_code or "",
                    v.color or "",
                    v.size or "",
                    v.additional_info or "",
                ]
                for v in variants
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[PRODUCT_VARIANT_GRID] Error: %s", exc)
            datagrid.set_data([])

    # ------------------------------------------------------------------ #
    # Closure-detail / receipts grid helpers                              #
    # ------------------------------------------------------------------ #

    def _populate_closure_detail_grid(self, datagrid):
        """Fill the CLOSURE_DETAIL grid with key/value rows for the selected closure."""
        datagrid.set_columns(["Field", "Value"])
        closure_id = getattr(self.app, "current_closure_id", None)
        if not closure_id:
            datagrid.set_data([])
            return
        try:
            from uuid import UUID as _UUID
            from data_layer.model import Closure, Cashier

            if isinstance(closure_id, str):
                closure_id = _UUID(closure_id)
            closure = Closure.get_by_id(closure_id)
            if not closure:
                datagrid.set_data([])
                return

            def _num(val):
                if val is None:
                    return "0.00"
                try:
                    return f"{float(val):.2f}"
                except (TypeError, ValueError):
                    return str(val)

            opened_by = ""
            if getattr(closure, "fk_cashier_opened_id", None):
                c = Cashier.get_by_id(closure.fk_cashier_opened_id)
                if c:
                    opened_by = c.user_name or ""
            closed_by = ""
            if getattr(closure, "fk_cashier_closed_id", None):
                c = Cashier.get_by_id(closure.fk_cashier_closed_id)
                if c:
                    closed_by = c.user_name or ""
            start_str = closure.closure_start_time.strftime("%Y-%m-%d %H:%M:%S") if closure.closure_start_time else ""
            end_str = closure.closure_end_time.strftime("%Y-%m-%d %H:%M:%S") if closure.closure_end_time else ""

            rows = [
                ["Closure No",              str(closure.closure_number or "")],
                ["Unique ID",               closure.closure_unique_id or ""],
                ["Date",                    str(closure.closure_date or "")],
                ["Start Time",              start_str],
                ["End Time",                end_str],
                ["Opened By",               opened_by],
                ["Closed By",               closed_by],
                ["Total Documents",         str(closure.total_document_count or 0)],
                ["Valid Transactions",       str(closure.valid_transaction_count or 0)],
                ["Cancelled Transactions",  str(closure.canceled_transaction_count or 0)],
                ["Return Transactions",     str(closure.return_transaction_count or 0)],
                ["Suspended Transactions",  str(closure.suspended_transaction_count or 0)],
                ["Gross Sales",             _num(closure.gross_sales_amount)],
                ["Net Sales",               _num(closure.net_sales_amount)],
                ["Total Tax",               _num(closure.total_tax_amount)],
                ["Total Discount",          _num(closure.total_discount_amount)],
                ["Total Tip",               _num(closure.total_tip_amount)],
                ["Opening Cash",            _num(closure.opening_cash_amount)],
                ["Closing Cash",            _num(closure.closing_cash_amount)],
                ["Expected Cash",           _num(closure.expected_cash_amount)],
                ["Cash Difference",         _num(closure.cash_difference)],
            ]
            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[CLOSURE_DETAIL_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _populate_closure_receipts_grid(self, datagrid):
        """Fill the CLOSURE_RECEIPTS grid with transaction heads for the selected closure."""
        datagrid.set_columns([
            "Receipt No", "Date/Time", "Type", "Total", "Payment", "Change", "Status"
        ])
        closure_id = getattr(self.app, "current_closure_id", None)
        if not closure_id:
            datagrid.set_data([])
            datagrid._receipt_ids = []
            return
        try:
            from uuid import UUID as _UUID
            from data_layer.model import Closure, TransactionHead

            if isinstance(closure_id, str):
                closure_id = _UUID(closure_id)
            closure = Closure.get_by_id(closure_id)
            if not closure:
                datagrid.set_data([])
                datagrid._receipt_ids = []
                return

            heads = TransactionHead.filter_by(
                closure_number=closure.closure_number,
                is_deleted=False,
            ) or []
            heads = sorted(
                heads,
                key=lambda h: h.transaction_date_time if h.transaction_date_time else h.receipt_number,
            )

            def _num(val):
                return "0.00" if val is None else f"{float(val):.2f}"

            data_rows = []
            receipt_ids = []
            for head in heads:
                dt_str = head.transaction_date_time.strftime("%Y-%m-%d %H:%M") if head.transaction_date_time else ""
                data_rows.append([
                    str(head.receipt_number or ""), dt_str,
                    head.document_type or "",
                    _num(head.total_amount), _num(head.total_payment_amount),
                    _num(head.total_change_amount), head.transaction_status or "",
                ])
                receipt_ids.append(str(head.id))

            datagrid.set_data(data_rows)
            datagrid._receipt_ids = receipt_ids
        except Exception as exc:
            logger.exception("[CLOSURE_RECEIPTS_GRID] Error: %s", exc)
            datagrid.set_data([])
            datagrid._receipt_ids = []

    def _populate_customer_activity_grid(self, datagrid):
        """
        Fill ``CUSTOMER_ACTIVITY_GRID`` on ``CUSTOMER_DETAIL`` with permanent
        ``TransactionHead`` rows where ``fk_customer_id`` matches
        ``app.current_customer_id`` (newest first, capped at 500 rows).
        """
        datagrid.set_columns([
            "Receipt No", "Closure No", "Date/Time", "Type",
            "Total", "Payment", "Change", "Status",
        ])
        customer_id = getattr(self.app, "current_customer_id", None)
        if not customer_id:
            datagrid.set_data([])
            datagrid._customer_transaction_head_ids = []
            return
        try:
            from uuid import UUID as _UUID
            from data_layer.model import TransactionHead

            cid = _UUID(str(customer_id)) if not isinstance(customer_id, _UUID) else customer_id
            heads = TransactionHead.filter_by(
                fk_customer_id=cid,
                is_deleted=False,
            ) or []

            def _ts(h):
                if h.transaction_date_time:
                    try:
                        return h.transaction_date_time.timestamp()
                    except (TypeError, ValueError, OSError):
                        pass
                return 0.0

            heads = sorted(
                heads,
                key=lambda h: (_ts(h), h.closure_number or 0, h.receipt_number or 0),
                reverse=True,
            )[:500]

            def _num(val):
                return "0.00" if val is None else f"{float(val):.2f}"

            data_rows = []
            head_ids = []
            for head in heads:
                dt_str = (
                    head.transaction_date_time.strftime("%Y-%m-%d %H:%M")
                    if head.transaction_date_time
                    else ""
                )
                data_rows.append([
                    str(head.receipt_number or ""),
                    str(head.closure_number or ""),
                    dt_str,
                    head.document_type or "",
                    _num(head.total_amount),
                    _num(head.total_payment_amount),
                    _num(head.total_change_amount),
                    head.transaction_status or "",
                ])
                head_ids.append(str(head.id))

            datagrid.set_data(data_rows)
            datagrid._customer_transaction_head_ids = head_ids
        except Exception as exc:
            logger.exception("[CUSTOMER_ACTIVITY_GRID] Error: %s", exc)
            datagrid.set_data([])
            datagrid._customer_transaction_head_ids = []

    def _populate_customer_loyalty_points_grid(self, datagrid):
        """
        Fill ``CUSTOMER_LOYALTY_POINTS_GRID`` with ``LoyaltyPointTransaction`` rows
        for ``app.current_customer_id`` (newest first, capped at 500).
        """
        datagrid.set_columns([
            "Date/Time",
            "Type",
            "Points",
            "Balance after",
            "Receipt",
            "Description",
        ])
        customer_id = getattr(self.app, "current_customer_id", None)
        if not customer_id:
            datagrid.set_data([])
            return
        try:
            from uuid import UUID as _UUID

            from data_layer.engine import Engine
            from data_layer.model.definition.loyalty_point_transaction import LoyaltyPointTransaction
            from data_layer.model.definition.transaction_head import TransactionHead

            cid = _UUID(str(customer_id)) if not isinstance(customer_id, _UUID) else customer_id
            engine = Engine()
            with engine.get_session() as session:
                q = (
                    session.query(LoyaltyPointTransaction)
                    .filter(
                        LoyaltyPointTransaction.fk_customer_id == cid,
                        LoyaltyPointTransaction.is_deleted != True,
                    )
                    .order_by(LoyaltyPointTransaction.transaction_date.desc())
                )
                ledger_rows = q.limit(500).all()
                data_rows = []
                for row in ledger_rows:
                    dt_str = (
                        row.transaction_date.strftime("%Y-%m-%d %H:%M")
                        if row.transaction_date
                        else ""
                    )
                    receipt_no = ""
                    if row.fk_transaction_head_id:
                        head = (
                            session.query(TransactionHead)
                            .filter(TransactionHead.id == row.fk_transaction_head_id)
                            .first()
                        )
                        if head:
                            receipt_no = str(head.receipt_number or "")
                    desc = row.description or row.notes or ""
                    if len(desc) > 120:
                        desc = desc[:117] + "..."
                    data_rows.append([
                        dt_str,
                        row.transaction_type or "",
                        str(row.points_amount),
                        str(row.balance_after),
                        receipt_no,
                        desc,
                    ])
                datagrid.set_data(data_rows)
        except Exception as exc:
            logger.exception("[CUSTOMER_LOYALTY_POINTS_GRID] Error: %s", exc)
            datagrid.set_data([])

    def repopulate_customer_activity_grid(self):
        """Reload customer detail datagrids after ``current_customer_id`` changes (e.g. first SAVE on ADD)."""
        from data_layer.enums import ControlName
        try:
            for grid in self.findChildren(DataGrid):
                name = getattr(grid, "name", None)
                if name == ControlName.CUSTOMER_ACTIVITY_GRID.value:
                    self._populate_customer_activity_grid(grid)
                elif name == ControlName.CUSTOMER_LOYALTY_POINTS_GRID.value:
                    self._populate_customer_loyalty_points_grid(grid)
        except Exception as exc:
            logger.exception("[CUSTOMER_DETAIL grids] Refresh error: %s", exc)

    def _populate_closure_receipt_detail_grid(self, datagrid):
        """
        Fill the upper CLOSURE_RECEIPT_DETAIL_GRID with key/value header rows for the
        selected receipt. Line items are shown separately in CLOSURE_RECEIPT_ITEMS_GRID.

        Uses a direct session query to avoid detached-object UUID comparison issues.
        """
        datagrid.set_columns(["Field", "Value"])
        receipt_id = getattr(self.app, "current_receipt_id", None)
        if not receipt_id:
            datagrid.set_data([])
            return
        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.transaction_head import TransactionHead

            def _num(val):
                if val is None:
                    return "0.00"
                try:
                    return f"{float(val):.2f}"
                except (TypeError, ValueError):
                    return str(val)

            from uuid import UUID as _UUID
            receipt_uuid = _UUID(str(receipt_id)) if not isinstance(receipt_id, _UUID) else receipt_id
            engine = Engine()
            with engine.get_session() as session:
                head = session.query(TransactionHead).filter(
                    TransactionHead.id == receipt_uuid
                ).first()

                if not head:
                    datagrid.set_data([])
                    return

                dt_str = head.transaction_date_time.strftime("%Y-%m-%d %H:%M:%S") if head.transaction_date_time else ""

                rows = [
                    ["Receipt No",      str(head.receipt_number or "")],
                    ["Unique ID",       head.transaction_unique_id or ""],
                    ["Date/Time",       dt_str],
                    ["Document Type",   head.document_type or ""],
                    ["Trans. Type",     head.transaction_type or ""],
                    ["Status",          head.transaction_status or ""],
                    ["Closure No",      str(head.closure_number or "")],
                    ["Currency",        head.base_currency or ""],
                    ["Total Amount",    _num(head.total_amount)],
                    ["Tax Amount",      _num(head.total_vat_amount)],
                    ["Discount",        _num(head.total_discount_amount)],
                    ["Surcharge",       _num(head.total_surcharge_amount)],
                    ["Payment Total",   _num(head.total_payment_amount)],
                    ["Change",          _num(head.total_change_amount)],
                    ["Tip",             _num(head.tip_amount)],
                    [
                        "Loyalty — points earned",
                        str(int(head.loyalty_points_earned or 0)),
                    ],
                    [
                        "Loyalty — points redeemed",
                        str(int(head.loyalty_points_redeemed or 0)),
                    ],
                ]

            datagrid.set_data(rows)
        except Exception as exc:
            logger.exception("[CLOSURE_RECEIPT_DETAIL_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _populate_closure_receipt_items_grid(self, datagrid):
        """
        Fill the lower CLOSURE_RECEIPT_ITEMS_GRID with sold line items
        (TransactionProduct rows) for the selected receipt.

        Columns: #, Product, Code, Qty, Unit, Unit Price, Discount, VAT%, Total, Status
        Cancelled lines (is_cancel=True) are still shown but marked as "CANCELLED".

        Uses a direct session query with the receipt UUID as a string to avoid
        detached-object UUID comparison issues.
        """
        datagrid.set_columns([
            "#", "Product", "Code", "Qty", "Unit",
            "Unit Price", "Discount", "VAT%", "Total", "Status"
        ])
        receipt_id = getattr(self.app, "current_receipt_id", None)
        if not receipt_id:
            datagrid.set_data([])
            return
        try:
            from data_layer.engine import Engine
            from data_layer.model.definition.transaction_head import TransactionHead
            from data_layer.model.definition.transaction_product import TransactionProduct

            def _num(val, decimals=2):
                if val is None:
                    return "0.00"
                try:
                    return f"{float(val):.{decimals}f}"
                except (TypeError, ValueError):
                    return str(val)

            from uuid import UUID as _UUID
            from data_layer.model.definition.transaction_head import TransactionHead
            from data_layer.model.definition.transaction_head_temp import TransactionHeadTemp
            from data_layer.model.definition.transaction_product_temp import TransactionProductTemp
            receipt_uuid = _UUID(str(receipt_id)) if not isinstance(receipt_id, _UUID) else receipt_id
            engine = Engine()
            with engine.get_session() as session:
                # Primary: permanent transaction_product table
                products = (
                    session.query(TransactionProduct)
                    .filter(
                        TransactionProduct.fk_transaction_head_id == receipt_uuid,
                        TransactionProduct.is_deleted != True,
                    )
                    .order_by(TransactionProduct.line_no)
                    .all()
                )

                # Fallback: temp table using receipt_number + closure_number to find the
                # matching temp head (permanent finalization creates a new UUID for the head
                # so the FK in temp products points to the original temp head ID)
                if not products:
                    perm_head = session.query(TransactionHead).filter(
                        TransactionHead.id == receipt_uuid
                    ).first()
                    if perm_head:
                        temp_head = session.query(TransactionHeadTemp).filter(
                            TransactionHeadTemp.receipt_number == perm_head.receipt_number,
                            TransactionHeadTemp.closure_number == perm_head.closure_number,
                        ).first()
                        if temp_head:
                            products = (
                                session.query(TransactionProductTemp)
                                .filter(
                                    TransactionProductTemp.fk_transaction_head_id == temp_head.id,
                                    TransactionProductTemp.is_deleted != True,
                                )
                                .order_by(TransactionProductTemp.line_no)
                                .all()
                            )

                data_rows = []
                for prod in products:
                    status = "CANCELLED" if getattr(prod, "is_cancel", False) else "OK"
                    data_rows.append([
                        str(prod.line_no or ""),
                        prod.product_name or "",
                        prod.product_code or "",
                        _num(prod.quantity, 3),
                        prod.unit_of_measure or "EA",
                        _num(prod.unit_price),
                        _num(prod.unit_discount),
                        _num(prod.vat_rate, 1),
                        _num(prod.total_price),
                        status,
                    ])

            datagrid.set_data(data_rows)
        except Exception as exc:
            logger.exception("[CLOSURE_RECEIPT_ITEMS_GRID] Error: %s", exc)
            datagrid.set_data([])

    def _create_button(self, design_data):
        """Create a button control with event binding and optional PLU text."""
        # Resolve parent: panel content widget or dialog
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        font_name = design_data.get("font", "Verdana")
        font_auto_height = design_data.get("font_auto_height", True)
        button = Button("", parent_widget, font_name=font_name, font_auto_height=font_auto_height)
        button.setGeometry(design_data["location_x"], design_data["location_y"],
                          design_data["width"], design_data["height"])
        button.set_color(design_data['background_color'], design_data['foreground_color'])
        button.setToolTip(design_data.get("caption", ""))
        button.setText(design_data.get("caption", ""))
        
        button_name = design_data.get("name", "")
        button.control_name = button_name
        function_name = design_data.get("function", "NONE")
        function2_name = design_data.get("function2")
        caption2 = design_data.get("caption2")
        event_handler = self.app.event_distributor(function_name)

        payment_events = ["CASH_PAYMENT", "CREDIT_PAYMENT", "CHECK_PAYMENT", "EXCHANGE_PAYMENT",
                         "PREPAID_PAYMENT", "CHARGE_SALE_PAYMENT", "OTHER_PAYMENT", "CHANGE_PAYMENT"]
        sale_events = ["SALE_PLU_CODE", "SALE_PLU_BARCODE", "SALE_DEPARTMENT"]
        quantity_events = ["INPUT_QUANTITY", "PLU_INQUIRY"]

        # Dual-function mode: requires function2, caption2, and function1 must not be a
        # sale/PLU event (those buttons derive their text from product data, not caption1)
        is_dual_function = (
            bool(function2_name) and bool(caption2)
            and function_name not in sale_events
        )

        if is_dual_function:
            handler2 = self.app.event_distributor(function2_name)
            caption1 = design_data.get("caption", "")
            button.setup_dual_function(
                caption1,
                caption2,
                event_handler,
                handler2,
                after_action_reset=self._reset_all_dual_buttons_to_primary,
            )
            self._dual_function_buttons.append(button)
        elif button_name == "FUNC":
            # FUNC switches labels only; each press flips all dual-function buttons
            # on this dialog between state 1 and state 2.
            def _func_click(checked=False, win=self):
                win._func_mode_active = not win._func_mode_active
                for btn in win._dual_function_buttons:
                    btn.toggle_state()
            button.clicked.connect(_func_click)
        elif event_handler:
            if (
                function_name in sale_events
                or function_name in payment_events
                or function_name in quantity_events
            ):
                button.clicked.connect(lambda checked=False, btn=button: event_handler(btn))
            elif function_name.startswith("NAVIGATE_TO_FORM:"):
                parts = function_name.split(':')
                if len(parts) >= 3:
                    target_form_id = parts[1]
                    transition_mode = parts[2]
                    button.clicked.connect(
                        lambda: self.app._navigate_to_form(target_form_id, transition_mode)
                    )
            elif function_name == "CLOSE_FORM":
                button.clicked.connect(self.accept)
            else:
                button.clicked.connect(event_handler)
        
        # PLU button text from product data
        if function_name in ["SALE_PLU_CODE", "SALE_PLU_BARCODE"] and button_name and button_name.upper().startswith("PLU"):
            try:
                code_or_barcode = button_name[3:]
                if function_name == "SALE_PLU_CODE":
                    products = [
                        p for p in self.app.product_data.get("Product", [])
                        if p.code == code_or_barcode and not (hasattr(p, 'is_deleted') and p.is_deleted)
                    ]
                    if products:
                        product = products[0]
                        product_name = product.short_name if product.short_name else product.name
                        button.setText(product_name)
                elif function_name == "SALE_PLU_BARCODE":
                    barcode_records = [
                        pb for pb in self.app.product_data.get("ProductBarcode", [])
                        if pb.barcode == code_or_barcode and not (hasattr(pb, 'is_deleted') and pb.is_deleted)
                    ]
                    if barcode_records:
                        product_barcode = barcode_records[0]
                        products = [
                            p for p in self.app.product_data.get("Product", [])
                            if p.id == product_barcode.fk_product_id
                        ]
                        if products:
                            product = products[0]
                            product_name = product.short_name if product.short_name else product.name
                            button.setText(product_name)
            except Exception:
                pass
        
        if font_auto_height and hasattr(button, '_adjust_font_size'):
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: button._adjust_font_size())
        
        if parent_panel:
            parent_panel.add_child_control(button)
    
    def _create_numpad(self, design_data):
        """Create a numpad control."""
        # Use width and height directly from database/design_data
        # NumPad now handles dynamic sizing internally
        width = design_data.get("width", 300)
        height = design_data.get("height", 350)
        
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        
        numpad = NumPad(self,
                        width=width,
                        height=height,
                        location_x=design_data["location_x"],
                        location_y=design_data["location_y"],
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        numpad.setToolTip(design_data.get("caption", ""))
        numpad.set_enter_event(self.app.event_distributor(design_data.get("function", "NONE")))
    
    def _create_payment_list(self, design_data):
        """Create a payment list control."""
        width = design_data.get("width", 970)
        height = design_data.get("height", 315)
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        location_x = design_data.get("location_x", 10)
        location_y = design_data.get("location_y", 100)
        
        self.payment_list = PaymentList(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        if "function" in design_data and design_data["function"]:
            self.payment_list.set_event(self.app.event_distributor(design_data["function"]))
    
    def _create_sale_list(self, design_data):
        """Create a sale list control."""
        width = design_data.get("width", 970)
        height = design_data.get("height", 315)
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        location_x = design_data.get("location_x", 10)
        location_y = design_data.get("location_y", 100)
        
        self.sale_list = SaleList(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        if "function" in design_data and design_data["function"]:
            self.sale_list.set_event(self.app.event_distributor(design_data["function"]))
    
    def _create_amount_table(self, design_data):
        """Create an amount table control."""
        width = design_data.get("width", 250)
        height = design_data.get("height", 200)
        background_color = design_data.get("background_color", 0x778D45)
        foreground_color = design_data.get("foreground_color", 0xFFFFFF)
        location_x = design_data.get("location_x", 1)
        location_y = design_data.get("location_y", 1)
        
        self.amount_table = AmountTable(self,
                        width=width,
                        height=height,
                        location_x=location_x,
                        location_y=location_y,
                        background_color=background_color,
                        foreground_color=foreground_color)
        
        if "function" in design_data and design_data["function"]:
            self.amount_table.set_event(self.app.event_distributor(design_data["function"]))
    
    def _create_label(self, design_data):
        """Create a label control."""
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        label = Label(parent_widget)
        label.setText(design_data.get('caption', ''))
        label.setGeometry(design_data["location_x"], design_data["location_y"],
                         design_data["width"], design_data["height"])
        
        if design_data.get('text_alignment') == "LEFT":
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        elif design_data.get('text_alignment') == "RIGHT":
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        elif design_data.get('text_alignment') == "CENTER":
            label.setAlignment(Qt.AlignCenter)
        else:
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        label.set_color(design_data.get('background_color', 0xFFFFFF),
                        design_data.get('foreground_color', 0x000000))
        
        if design_data.get('font_size'):
            from PySide6.QtGui import QFont
            font = label.font()
            font.setPointSize(int(design_data['font_size']))
            label.setFont(font)
        
        if design_data.get('caption'):
            label.setToolTip(design_data['caption'])
        
        if parent_panel:
            parent_panel.add_child_control(label)

    def _create_textbox(self, design_data):
        """Create a textbox control with optional panel parent and CurrentData loading."""
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        textbox = TextBox(parent_widget)
        alignment = design_data.get('alignment', 'left').lower()
        if alignment == "left":
            textbox.setAlignment(Qt.AlignLeft)
        elif alignment == "right":
            textbox.setAlignment(Qt.AlignRight)
        elif alignment == "center":
            textbox.setAlignment(Qt.AlignCenter)
        if design_data.get('input_type') == "password":
            textbox.set_password_type()
        
        textbox_name = design_data.get('name') or design_data.get('field_name')
        textbox.__name__ = textbox_name
        textbox.name = textbox_name
        textbox.setGeometry(design_data["location_x"], design_data["location_y"],
                            design_data["width"], design_data["height"])
        textbox.set_font_size(design_data.get('font_size'))
        textbox.field_name = design_data.get('caption')
        if design_data.get('place_holder'):
            textbox.setPlaceholderText(design_data.get('place_holder'))
        textbox.set_color(design_data['background_color'], design_data['foreground_color'])
        if design_data.get('use_keyboard') or parent_panel:
            textbox.keyboard = self.keyboard
        
        if parent_panel:
            parent_panel.add_child_control(textbox)
        
        # Load from CurrentData when textbox is in a panel
        if parent_panel and getattr(parent_panel, 'name', None):
            panel_name = parent_panel.name
            if textbox_name:
                field_name = textbox_name.lower()
                parts = panel_name.lower().split('_')
                model_class_name = ''.join(word.capitalize() for word in parts)
                model_instance = None
                cache_attr_name = None
                if model_class_name == "PosSettings":
                    cache_attr_name = "pos_settings"
                elif model_class_name == "Cashier":
                    cache_attr_name = "cashier_data"
                if cache_attr_name and hasattr(self.app, cache_attr_name):
                    model_instance = getattr(self.app, cache_attr_name)
                    if model_instance and hasattr(model_instance, 'unwrap'):
                        model_instance = model_instance.unwrap()
                if not model_instance and model_class_name == "Product":
                    # Load from current_product_id for the PRODUCT panel in PRODUCT_DETAIL
                    try:
                        from uuid import UUID as _UUID
                        from data_layer.model.definition.product import Product as _Product
                        product_id = getattr(self.app, 'current_product_id', None)
                        if product_id:
                            if isinstance(product_id, str):
                                product_id = _UUID(product_id)
                            model_instance = _Product.get_by_id(product_id)
                    except Exception:
                        pass
                if not model_instance and model_class_name == "Customer":
                    # Load from current_customer_id for the CUSTOMER panel in CUSTOMER_DETAIL.
                    # Skip entirely when _customer_add_mode is True (ADD button) so the panel
                    # stays blank and the cashier can fill in fresh data.
                    if not getattr(self.app, '_customer_add_mode', False):
                        try:
                            from uuid import UUID as _UUID
                            from data_layer.model.definition.customer import Customer as _Customer
                            customer_id = getattr(self.app, 'current_customer_id', None)
                            if customer_id:
                                if isinstance(customer_id, str):
                                    customer_id = _UUID(customer_id)
                                model_instance = _Customer.get_by_id(customer_id)
                        except Exception:
                            pass
                if not model_instance and model_class_name != "Customer":
                    # For non-Customer panels use the generic first-record fallback.
                    # Customer panels are intentionally excluded to avoid loading Walk-in
                    # data when no specific customer is selected (e.g., ADD mode).
                    try:
                        import data_layer.model.definition as model_module
                        from data_layer.model.definition import __all__ as model_names
                        if model_class_name in model_names:
                            model_class = getattr(model_module, model_class_name)
                            instances = model_class.get_all(is_deleted=False)
                            if instances:
                                model_instance = instances[0]
                    except Exception:
                        pass
                if model_instance:
                    try:
                        value = getattr(model_instance, field_name, None)
                        if value is not None:
                            textbox.setText(str(value))
                    except Exception:
                        pass

    def _create_checkbox(self, design_data):
        """Create a checkbox with the same panel/model loading rules as this dialog's textboxes."""
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self

        checkbox = CheckBox(parent_widget)
        cb_name = design_data.get('name') or design_data.get('field_name')
        checkbox.__name__ = cb_name
        checkbox.name = cb_name
        checkbox.setGeometry(
            design_data["location_x"],
            design_data["location_y"],
            design_data["width"],
            design_data["height"],
        )
        checkbox.set_font_size(design_data.get('font_size'))
        checkbox.field_name = design_data.get('caption', '')
        if design_data.get('caption'):
            checkbox.setText(design_data['caption'])
        checkbox.set_color(
            design_data.get('background_color', 0xFFFFFF),
            design_data.get('foreground_color', 0x000000),
        )
        if parent_panel:
            parent_panel.add_child_control(checkbox)

        if parent_panel and getattr(parent_panel, 'name', None) and cb_name:
            panel_name = parent_panel.name
            field_name = cb_name.lower()
            parts = panel_name.lower().split('_')
            model_class_name = ''.join(word.capitalize() for word in parts)
            model_instance = None
            cache_attr_name = None
            if model_class_name == "PosSettings":
                cache_attr_name = "pos_settings"
            elif model_class_name == "Cashier":
                cache_attr_name = "cashier_data"
            if cache_attr_name and hasattr(self.app, cache_attr_name):
                model_instance = getattr(self.app, cache_attr_name)
                if model_instance and hasattr(model_instance, 'unwrap'):
                    model_instance = model_instance.unwrap()
            if not model_instance and model_class_name == "Product":
                try:
                    from uuid import UUID as _UUID
                    from data_layer.model.definition.product import Product as _Product
                    product_id = getattr(self.app, 'current_product_id', None)
                    if product_id:
                        if isinstance(product_id, str):
                            product_id = _UUID(product_id)
                        model_instance = _Product.get_by_id(product_id)
                except Exception:
                    pass
            if not model_instance and model_class_name == "Customer":
                if not getattr(self.app, '_customer_add_mode', False):
                    try:
                        from uuid import UUID as _UUID
                        from data_layer.model.definition.customer import Customer as _Customer
                        customer_id = getattr(self.app, 'current_customer_id', None)
                        if customer_id:
                            if isinstance(customer_id, str):
                                customer_id = _UUID(customer_id)
                            model_instance = _Customer.get_by_id(customer_id)
                    except Exception:
                        pass
            if not model_instance and model_class_name != "Customer":
                try:
                    import data_layer.model.definition as model_module
                    from data_layer.model.definition import __all__ as model_names
                    if model_class_name in model_names:
                        model_class = getattr(model_module, model_class_name)
                        instances = model_class.get_all(is_deleted=False)
                        if instances:
                            model_instance = instances[0]
                except Exception:
                    pass
            if model_instance:
                try:
                    value = getattr(model_instance, field_name, None)
                    checkbox.setChecked(bool(value) if value is not None else False)
                except Exception:
                    pass
    
    def _create_combobox(self, design_data):
        """Create a combobox control with optional panel parent and item source."""
        parent_panel = None
        if design_data.get('parent_name'):
            parent_panel = self._panels.get(design_data['parent_name'])
        parent_widget = parent_panel.get_content_widget() if parent_panel else self
        
        width = design_data.get("width", 240)
        height = design_data.get("height", 44)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)
        
        combo = ComboBox(parent_widget,
                         width=width,
                         height=height,
                         location_x=design_data.get("location_x", 0),
                         location_y=design_data.get("location_y", 0),
                         background_color=background_color,
                         foreground_color=foreground_color,
                         font_size=design_data.get("font_size", 20))
        
        items = design_data.get("items")
        if items and isinstance(items, list):
            combo.set_items([str(x) for x in items])
        else:
            from data_layer.enums import ControlName, EventName
            name_key = str(design_data.get("name", ""))
            if name_key == ControlName.CASHIER_NAME_LIST.value:
                try:
                    from data_layer.model import Cashier
                    cashiers = Cashier.get_all(is_deleted=False)
                    labels = [f"{c.user_name} ({c.name} {c.last_name})" for c in cashiers]
                    if design_data.get("function1") == EventName.LOGIN.value:
                        labels.append("SUPERVISOR")
                    combo.set_items(labels)
                except Exception:
                    combo.set_items([])
        
        if design_data.get("function"):
            combo.set_event(self.app.event_distributor(design_data["function"]))
        if design_data.get("caption"):
            combo.setToolTip(design_data["caption"])
        if design_data.get("name") is not None:
            combo.name = design_data["name"]
        if design_data.get("type_name") is not None:
            combo.type = design_data["type_name"]
        if design_data.get("function1") is not None:
            combo.function1 = design_data["function1"]
        if design_data.get("function2") is not None:
            combo.function2 = design_data["function2"]
        
        if parent_panel:
            parent_panel.add_child_control(combo)
    
    def _create_datagrid(self, design_data):
        """
        Create a DataGrid control for displaying tabular data.

        If ``design_data`` contains a ``tab_id`` key the grid is parented to the
        corresponding tab-page ``QWidget`` (looked up in ``self._tab_pages``).
        Otherwise it is parented directly to this dialog.

        Args:
            design_data (dict): Design specifications for the datagrid
        """
        width = design_data.get("width", 600)
        height = design_data.get("height", 400)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)

        # Resolve parent: tab page or dialog
        parent_widget = self
        tab_id = design_data.get("tab_id")
        if tab_id and hasattr(self, "_tab_pages"):
            tab_page = self._tab_pages.get(tab_id)
            if tab_page:
                parent_widget = tab_page

        datagrid = DataGrid(parent_widget)
        # If the parent tab page has a layout, add the DataGrid to it so it
        # stretches to fill the page.  Otherwise fall back to absolute geometry.
        if parent_widget is not self and parent_widget.layout() is not None:
            parent_widget.layout().addWidget(datagrid)
        else:
            datagrid.setGeometry(
                design_data.get("location_x", 0),
                design_data.get("location_y", 0),
                width,
                height
            )
        datagrid.set_color(background_color, foreground_color)

        if "font_size" in design_data:
            from PySide6.QtGui import QFont
            font = QFont("Verdana", design_data["font_size"])
            datagrid.setFont(font)

        if "name" in design_data:
            datagrid.name = design_data["name"]
        if "function" in design_data:
            datagrid.function = design_data["function"]
        if "caption" in design_data:
            datagrid.setToolTip(design_data["caption"])

        from data_layer.enums import ControlName
        name_key = str(design_data.get("name", ""))

        if name_key == ControlName.CLOSURE.value:
            try:
                from data_layer.model import Closure, Cashier
                closures = Closure.get_all(is_deleted=False)
                closures = sorted(
                    closures,
                    key=lambda c: c.closure_start_time if c.closure_start_time else c.closure_date,
                    reverse=True
                )
                datagrid.set_columns([
                    "Closure No", "Date", "Cashier",
                    "Gross Sales", "Opening Cash", "Closing Cash"
                ])
                data_rows = []
                closure_ids = []
                for closure in closures:
                    cashier_name = ""
                    if closure.fk_cashier_closed_id:
                        cashier = Cashier.get_by_id(closure.fk_cashier_closed_id)
                        if cashier:
                            cashier_name = cashier.user_name or ""
                    date_str = ""
                    if closure.closure_start_time:
                        date_str = closure.closure_start_time.strftime("%Y-%m-%d %H:%M")
                    elif closure.closure_date:
                        date_str = closure.closure_date.strftime("%Y-%m-%d")
                    def _num(val):
                        return "0.00" if val is None else f"{float(val):.2f}"
                    row = [
                        str(closure.closure_number), date_str, cashier_name,
                        _num(closure.gross_sales_amount),
                        _num(closure.opening_cash_amount),
                        _num(closure.closing_cash_amount)
                    ]
                    data_rows.append(row)
                    closure_ids.append(str(closure.id))
                datagrid.set_data(data_rows)
                datagrid._closure_ids = closure_ids
            except Exception as e:
                logger.exception("Error loading closure data: %s", e)
                datagrid.set_columns(["No Data Available"])
                datagrid.set_data([])
                datagrid._closure_ids = []

        elif name_key == ControlName.CLOSURE_DETAIL_GRID.value:
            self._populate_closure_detail_grid(datagrid)

        elif name_key == ControlName.CLOSURE_RECEIPTS_DATAGRID.value:
            self._populate_closure_receipts_grid(datagrid)

        elif name_key == ControlName.CLOSURE_RECEIPT_DETAIL_GRID.value:
            self._populate_closure_receipt_detail_grid(datagrid)

        elif name_key == ControlName.CLOSURE_RECEIPT_ITEMS_GRID.value:
            self._populate_closure_receipt_items_grid(datagrid)

        elif name_key == ControlName.SUSPENDED_SALES_DATAGRID.value:
            try:
                cols, data_rows = self.app.get_suspended_market_receipt_rows()
                datagrid.set_columns(cols)
                datagrid.set_data(data_rows)
                datagrid.setColumnHidden(0, True)
            except Exception as e:
                logger.exception("Error loading suspended sales list: %s", e)
                datagrid.set_columns(["No Data Available"])
                datagrid.set_data([])

        elif name_key == ControlName.PRODUCT_INFO_GRID.value:
            self._populate_product_info_grid(datagrid)

        elif name_key == ControlName.PRODUCT_BARCODE_GRID.value:
            self._populate_product_barcode_grid(datagrid)

        elif name_key == ControlName.PRODUCT_ATTRIBUTE_GRID.value:
            self._populate_product_attribute_grid(datagrid)

        elif name_key == ControlName.PRODUCT_VARIANT_GRID.value:
            self._populate_product_variant_grid(datagrid)

        elif name_key == ControlName.CUSTOMER_ACTIVITY_GRID.value:
            self._populate_customer_activity_grid(datagrid)

        elif name_key == ControlName.CUSTOMER_LOYALTY_POINTS_GRID.value:
            self._populate_customer_loyalty_points_grid(datagrid)

        datagrid.show()

    def _create_panel(self, design_data):
        """
        Create a Panel control with scrollbar support.

        If ``design_data`` contains a ``tab_id`` key the panel is parented to
        the matching tab-page ``QWidget`` (looked up in ``self._tab_pages``) and
        added to its layout so it fills the tab area.  Otherwise the panel is
        parented directly to this dialog.

        Args:
            design_data (dict): Design specifications for the panel
        """
        width = design_data.get("width", 800)
        height = design_data.get("height", 600)
        background_color = design_data.get("background_color", 0xFFFFFF)
        foreground_color = design_data.get("foreground_color", 0x000000)

        # Resolve parent: tab page or dialog
        parent_widget = self
        tab_id = design_data.get("tab_id")
        if tab_id and hasattr(self, "_tab_pages"):
            tab_page = self._tab_pages.get(tab_id)
            if tab_page:
                parent_widget = tab_page

        panel = Panel(
            parent_widget,
            width=width,
            height=height,
            location_x=design_data.get("location_x", 0),
            location_y=design_data.get("location_y", 0),
            background_color=background_color,
            foreground_color=foreground_color
        )

        if "name" in design_data:
            panel.name = design_data["name"]
            if not hasattr(self, '_panels'):
                self._panels = {}
            self._panels[design_data["name"]] = panel

        # If parented to a tab page that has a layout, add panel to it so it
        # stretches to fill the tab content area automatically.
        if parent_widget is not self and parent_widget.layout() is not None:
            parent_widget.layout().addWidget(panel)

        panel.show()


"""
Campaign list and detail events (administrators).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID

from data_layer.enums import ControlName, EventName, FormName

from core.logger import get_logger

logger = get_logger(__name__)


class CampaignEvent:
    """Handlers for CAMPAIGN_LIST and CAMPAIGN_DETAIL dynamic forms."""

    def _require_admin_campaign_access(self) -> bool:
        logged_in = getattr(self, "cashier_data", None)
        if logged_in and hasattr(logged_in, "unwrap"):
            logged_in = logged_in.unwrap()
        if not logged_in or not getattr(logged_in, "is_administrator", False):
            try:
                from user_interface.form.message_form import MessageForm

                win = getattr(self.interface, "window", None)
                if win:
                    MessageForm.show_error(
                        win,
                        "Only administrators can manage campaigns.",
                        "Access denied",
                    )
            except Exception:
                pass
            logger.warning("[CAMPAIGN] Access denied — not an administrator")
            return False
        return True

    def _campaign_list_form_event(self) -> bool:
        if not self.login_succeed:
            self._logout_event()
            return False
        if not self._require_admin_campaign_access():
            return False
        self.current_form_type = FormName.CAMPAIGN_LIST
        self.interface.redraw(form_name=FormName.CAMPAIGN_LIST.name)
        return True

    def _campaign_search_event(self) -> bool:
        if not self.login_succeed:
            return False
        if not self._require_admin_campaign_access():
            return False
        try:
            from sqlalchemy import or_

            from user_interface.control import DataGrid, TextBox

            from data_layer.engine import Engine
            from data_layer.model.definition.campaign import Campaign

            window = self.interface.window
            if not window:
                logger.error("[CAMPAIGN_SEARCH] Window not available")
                return False

            search_term = ""
            for child in window.children():
                if isinstance(child, TextBox):
                    name = getattr(child, "name", "") or getattr(child, "__name__", "")
                    if name == ControlName.CAMPAIGN_SEARCH_TEXTBOX.value:
                        search_term = child.text().strip()
                        break

            engine = Engine()
            with engine.get_session() as session:
                q = session.query(Campaign).filter(Campaign.is_deleted.is_(False))
                if search_term:
                    like = f"%{search_term}%"
                    q = q.filter(
                        or_(
                            Campaign.code.ilike(like),
                            Campaign.name.ilike(like),
                        )
                    )
                rows = q.order_by(Campaign.code).limit(500).all()

            columns = ["Code", "Name", "Active", "Type id", "Priority", "Coupon"]
            grid_rows = []
            campaign_ids = []
            for c in rows:
                grid_rows.append(
                    [
                        c.code or "",
                        c.name or "",
                        "Y" if c.is_active else "N",
                        str(c.fk_campaign_type_id) if c.fk_campaign_type_id else "",
                        str(c.priority) if c.priority is not None else "",
                        "Y" if c.requires_coupon else "N",
                    ]
                )
                campaign_ids.append(str(c.id))

            for child in window.children():
                if isinstance(child, DataGrid):
                    if getattr(child, "name", "") == ControlName.CAMPAIGN_LIST_DATAGRID.value:
                        child.set_columns(columns)
                        child.set_data(grid_rows)
                        child._campaign_ids = campaign_ids
                        break

            logger.info("[CAMPAIGN_SEARCH] Listed %s campaign(s)", len(grid_rows))
            return True
        except Exception as exc:
            logger.error("[CAMPAIGN_SEARCH] Error: %s", exc)
            return False

    def _campaign_detail_event(self) -> bool:
        if not self.login_succeed:
            return False
        if not self._require_admin_campaign_access():
            return False
        try:
            from user_interface.control import DataGrid

            window = self.interface.window
            if not window:
                logger.error("[CAMPAIGN_DETAIL] Window not available")
                return False

            campaign_id = None
            for child in window.children():
                if isinstance(child, DataGrid):
                    if getattr(child, "name", "") == ControlName.CAMPAIGN_LIST_DATAGRID.value:
                        idx = child.get_selected_row_index()
                        ids = getattr(child, "_campaign_ids", [])
                        if 0 <= idx < len(ids):
                            campaign_id = ids[idx]
                        break

            if not campaign_id:
                logger.warning("[CAMPAIGN_DETAIL] No campaign selected")
                return False

            self.current_campaign_id = campaign_id
            self.interface.show_modal(form_name=FormName.CAMPAIGN_DETAIL.name)
            logger.info("[CAMPAIGN_DETAIL] Opened campaign id=%s", campaign_id)
            return True
        except Exception as exc:
            logger.error("[CAMPAIGN_DETAIL] Error: %s", exc)
            return False

    def _campaign_detail_save_event(self) -> bool:
        if not self.login_succeed:
            return False
        if not self._require_admin_campaign_access():
            return False

        def _parse_dt(raw: str):
            s = (raw or "").strip()
            if not s:
                return None
            s = s.replace("Z", "").replace("T", " ")
            if len(s) <= 10:
                try:
                    return datetime.strptime(s[:10], "%Y-%m-%d")
                except ValueError:
                    pass
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                try:
                    return datetime.strptime(s[:19], fmt)
                except ValueError:
                    continue
            try:
                return datetime.fromisoformat(s)
            except ValueError:
                return None

        def _parse_time(raw: str):
            s = (raw or "").strip()
            if not s:
                return None
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    return datetime.strptime(s, fmt).time()
                except ValueError:
                    continue
            return None

        def _parse_int(raw: str):
            s = (raw or "").strip()
            if not s:
                return None
            return int(s)

        def _parse_dec(raw: str):
            s = (raw or "").strip()
            if not s:
                return None
            return Decimal(s)

        try:
            active_dialogs = getattr(self.interface, "active_dialogs", [])
            if not active_dialogs:
                logger.error("[CAMPAIGN_DETAIL_SAVE] No active dialog")
                return False
            dialog = active_dialogs[-1]
            values = dialog.get_panel_textbox_values("CAMPAIGN")
            if not values:
                logger.warning("[CAMPAIGN_DETAIL_SAVE] No CAMPAIGN panel values")
                return False

            cid = getattr(self, "current_campaign_id", None)
            if not cid:
                logger.error("[CAMPAIGN_DETAIL_SAVE] current_campaign_id not set")
                return False
            if isinstance(cid, str):
                cid = UUID(cid)

            from data_layer.engine import Engine
            from data_layer.model.definition.campaign import Campaign

            engine = Engine()
            with engine.get_session() as session:
                camp = session.query(Campaign).filter(Campaign.id == cid).first()
                if not camp:
                    logger.error("[CAMPAIGN_DETAIL_SAVE] Campaign not found")
                    return False

                if "code" in values:
                    camp.code = (values["code"] or "").strip() or camp.code
                if "name" in values:
                    camp.name = (values["name"] or "").strip() or camp.name
                if "description" in values:
                    camp.description = values["description"] or None
                if "fk_campaign_type_id" in values:
                    t = (values["fk_campaign_type_id"] or "").strip()
                    if t:
                        camp.fk_campaign_type_id = UUID(t)
                if "discount_type" in values:
                    v = (values["discount_type"] or "").strip()
                    camp.discount_type = v or None
                for key, conv in (
                    ("discount_value", _parse_dec),
                    ("discount_percentage", _parse_dec),
                    ("max_discount_amount", _parse_dec),
                    ("min_purchase_amount", _parse_dec),
                    ("max_purchase_amount", _parse_dec),
                ):
                    if key in values:
                        try:
                            camp.__setattr__(key, conv(values[key]))
                        except (InvalidOperation, ValueError, TypeError):
                            pass
                for key in ("buy_quantity", "get_quantity"):
                    if key in values:
                        try:
                            camp.__setattr__(key, _parse_int(values[key]))
                        except (ValueError, TypeError):
                            pass
                if "start_date" in values:
                    camp.start_date = _parse_dt(values["start_date"])
                if "end_date" in values:
                    camp.end_date = _parse_dt(values["end_date"])
                if "start_time" in values:
                    camp.start_time = _parse_time(values["start_time"])
                if "end_time" in values:
                    camp.end_time = _parse_time(values["end_time"])
                if "days_of_week" in values:
                    v = (values["days_of_week"] or "").strip()
                    camp.days_of_week = v or None
                if "priority" in values:
                    try:
                        camp.priority = int((values["priority"] or "0").strip() or 0)
                    except ValueError:
                        pass
                for key in ("is_combinable", "is_active", "is_auto_apply", "requires_coupon"):
                    if key in values:
                        camp.__setattr__(
                            key,
                            str(values[key]).lower() in ("true", "1", "yes", "on"),
                        )
                for key in ("usage_limit_per_customer", "total_usage_limit"):
                    if key in values:
                        try:
                            camp.__setattr__(key, _parse_int(values[key]))
                        except (ValueError, TypeError):
                            pass
                if "total_usage_count" in values:
                    s = (values["total_usage_count"] or "").strip()
                    if s:
                        try:
                            camp.total_usage_count = int(s)
                        except ValueError:
                            pass
                if "notification_message" in values:
                    v = values["notification_message"] or ""
                    camp.notification_message = v or None

                session.commit()

            if hasattr(self, "refresh_active_campaign_cache"):
                self.refresh_active_campaign_cache()

            logger.info("[CAMPAIGN_DETAIL_SAVE] Saved campaign id=%s", cid)
            return True
        except Exception as exc:
            logger.error("[CAMPAIGN_DETAIL_SAVE] Error: %s", exc)
            return False

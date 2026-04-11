"""
Resolve LoyaltyProgram / LoyaltyProgramPolicy / LoyaltyRedemptionPolicy rows for the loyalty settings form.

Policy and redemption rows are matched to the same program chosen for the program tab.
"""

from __future__ import annotations

from typing import Any, Optional


def loyalty_program_for_settings() -> Optional[Any]:
    from data_layer.model.definition.loyalty_program import LoyaltyProgram

    rows = LoyaltyProgram.get_all(is_deleted=False) or []
    if not rows:
        return None
    active = [r for r in rows if getattr(r, "is_active", True)]
    return active[0] if active else rows[0]


def loyalty_policy_for_settings() -> Optional[Any]:
    from data_layer.model.definition.loyalty_program_policy import LoyaltyProgramPolicy

    prog = loyalty_program_for_settings()
    if not prog:
        return None
    pid = str(prog.id)
    for p in LoyaltyProgramPolicy.get_all(is_deleted=False) or []:
        if str(p.fk_loyalty_program_id) == pid:
            return p
    return None


def loyalty_redemption_for_settings() -> Optional[Any]:
    from data_layer.model.definition.loyalty_redemption_policy import LoyaltyRedemptionPolicy

    prog = loyalty_program_for_settings()
    if not prog:
        return None
    pid = str(prog.id)
    for p in LoyaltyRedemptionPolicy.get_all(is_deleted=False) or []:
        if str(p.fk_loyalty_program_id) == pid:
            return p
    return None


def get_settings_form_loyalty_instance(model_class_name: str) -> Optional[Any]:
    if model_class_name == "LoyaltyProgram":
        return loyalty_program_for_settings()
    if model_class_name == "LoyaltyProgramPolicy":
        return loyalty_policy_for_settings()
    if model_class_name == "LoyaltyRedemptionPolicy":
        return loyalty_redemption_for_settings()
    return None

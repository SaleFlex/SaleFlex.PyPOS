"""
SaleFlex.PyPOS - GATE API serializers package.

Each serializer converts a local ORM record (identified by UUID) into the
JSON payload format expected by the SaleFlex.GATE REST API.

Copyright (c) 2026 Ferhat Mousavi
"""

from pos.integration.gate.serializers.transaction_serializer import TransactionSerializer
from pos.integration.gate.serializers.closure_serializer import ClosureSerializer
from pos.integration.gate.serializers.product_serializer import ProductSerializer
from pos.integration.gate.serializers.warehouse_serializer import WarehouseSerializer
from pos.integration.gate.serializers.campaign_serializer import CampaignSerializer
from pos.integration.gate.serializers.notification_serializer import NotificationSerializer

__all__ = [
    "TransactionSerializer",
    "ClosureSerializer",
    "ProductSerializer",
    "WarehouseSerializer",
    "CampaignSerializer",
    "NotificationSerializer",
]

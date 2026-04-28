"""
SaleFlex.PyPOS - Database Initial Data
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

from data_layer.model import Cashier


from core.logger import get_logger

logger = get_logger(__name__)

def _insert_admin_cashier(session) -> Cashier:
    """
    Insert default cashiers if not exists.
    Creates admin user and a standard cashier for initial setup.
    """
    admin_exists = session.query(Cashier).filter_by(user_name="admin").first()
    if not admin_exists:
        admin_cashier = Cashier(
            no=1,
            user_name="admin",
            name="Ferhat",
            last_name="Mousavi",
            password="admin",  # TODO: Should be hashed in real application
            identity_number="A00001",
            description="System administrator",
            is_administrator=True,
            is_manager=False,
            is_active=True
        )
        session.add(admin_cashier)
        session.flush()  # To get the ID
        logger.info("✓ Default cashier 'Ferhat Mousavi' added (password: admin)")
    else:
        admin_cashier = admin_exists

    cashier_exists = session.query(Cashier).filter_by(user_name="jdoe").first()
    if not cashier_exists:
        standard_cashier = Cashier(
            no=2,
            user_name="jdoe",
            name="John",
            last_name="Doe",
            password="1234",
            identity_number="C00002",
            description="Standard cashier",
            is_administrator=False,
            is_manager=False,
            is_active=True
        )
        session.add(standard_cashier)
        session.flush()
        logger.info("✓ Default cashier 'John Doe' added (password: 1234)")

    return admin_cashier
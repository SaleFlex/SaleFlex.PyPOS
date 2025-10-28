"""
SaleFlex.PyPOS - Database Initial Data

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

from data_layer.model import Cashier

def _insert_admin_cashier(session) -> Cashier:
    """
    Insert default cashiers if not exists.
    Creates admin user for initial setup.
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
            is_active=True
        )
        session.add(admin_cashier)
        session.flush()  # To get the ID
        print("✓ Default cashier 'Ferhat Mousavi' added (password: admin)")
        return admin_cashier
    else:
        return admin_exists
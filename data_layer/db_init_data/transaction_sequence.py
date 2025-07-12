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

from data_layer.model import TransactionSequence


def _insert_transaction_sequences(session, admin_cashier_id: int):
    """Insert default transaction sequences if not exists"""
    sequence_exists = session.query(TransactionSequence).first()
    if not sequence_exists:
        sequences = [
            {"name": "ReceiptNumber", "value": 1, "description": "Receipt sequence number"},
            {"name": "ClosureNumber", "value": 1, "description": "Closure sequence number"}
        ]

        for seq_data in sequences:
            sequence = TransactionSequence(
                name=seq_data["name"],
                value=seq_data["value"],
                description=seq_data["description"]
            )
            sequence.fk_cashier_create_id = admin_cashier_id
            sequence.fk_cashier_update_id = admin_cashier_id
            session.add(sequence)
        print("✓ Default transaction sequences added")
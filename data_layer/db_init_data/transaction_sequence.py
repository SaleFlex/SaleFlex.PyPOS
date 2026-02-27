"""
SaleFlex.PyPOS - Database Initial Data

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

from data_layer.model import TransactionSequence



from core.logger import get_logger

logger = get_logger(__name__)

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
        logger.info("✓ Default transaction sequences added")
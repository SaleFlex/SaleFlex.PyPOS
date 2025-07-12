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

from data_layer.model import PaymentType


def _insert_payment_types(session):
    """Insert payment types if not exists"""
    payment_types_data = [
        {
            "type_no": 1,
            "type_name": "Cash",
            "type_description": "Cash payment",
            "culture_info": "en-GB"
        },
        {
            "type_no": 2,
            "type_name": "Credit Card",
            "type_description": "Credit card payment",
            "culture_info": "en-GB"
        },
        {
            "type_no": 3,
            "type_name": "Check",
            "type_description": "Check payment",
            "culture_info": "en-GB"
        },
        {
            "type_no": 4,
            "type_name": "Credit",
            "type_description": "Credit payment without card",
            "culture_info": "en-GB"
        },
        {
            "type_no": 5,
            "type_name": "Prepaid Card",
            "type_description": "Prepaid card payment",
            "culture_info": "en-GB"
        },
        {
            "type_no": 6,
            "type_name": "Mobile",
            "type_description": "Mobile payment",
            "culture_info": "en-GB"
        },
        {
            "type_no": 7,
            "type_name": "Bonus",
            "type_description": "Bonus payment",
            "culture_info": "en-GB"
        },
        {
            "type_no": 8,
            "type_name": "Foreign currency",
            "type_description": "Foreign currency payment",
            "culture_info": "en-GB"
        },
        {
            "type_no": 9,
            "type_name": "Payment on credit",
            "type_description": "Payment on credit",
            "culture_info": "en-GB"
        },
        {
            "type_no": 10,
            "type_name": "Other",
            "type_description": "Other payment methods",
            "culture_info": "en-GB"
        }
    ]

    for payment_type_data in payment_types_data:
        # Check if payment type already exists
        existing_payment_type = session.query(PaymentType).filter_by(
            type_no=payment_type_data["type_no"]
        ).first()
        
        if not existing_payment_type:
            payment_type = PaymentType(
                type_no=payment_type_data["type_no"],
                type_name=payment_type_data["type_name"],
                type_description=payment_type_data["type_description"]
            )
            payment_type.culture_info = payment_type_data["culture_info"]
            session.add(payment_type)
            print(f"✓ Payment type '{payment_type_data['type_name']}' added")
        else:
            print(f"✓ Payment type '{payment_type_data['type_name']}' already exists")

    session.flush() 
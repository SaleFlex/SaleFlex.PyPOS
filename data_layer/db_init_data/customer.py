"""
SaleFlex.PyPOS - Point of Sale Application
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

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from data_layer.model.definition.customer import Customer
from core.logger import get_logger

logger = get_logger(__name__)


def _migrate_is_walkin_column(session: Session):
    """
    Ensure the ``is_walkin`` column exists in the ``customer`` table.

    ``metadata.create_all()`` only creates missing tables — it does not alter
    existing ones.  If the database was initialised before this column was added
    to the model, the INSERT below would fail with an "unknown column" error and
    roll back the entire transaction.  This helper detects that situation and
    adds the column via ALTER TABLE so the seed can proceed safely.
    """
    try:
        bind = session.get_bind()
        inspector = inspect(bind)
        columns = [col["name"] for col in inspector.get_columns("customer")]
        if "is_walkin" not in columns:
            session.execute(text(
                "ALTER TABLE customer ADD COLUMN is_walkin BOOLEAN NOT NULL DEFAULT 0"
            ))
            session.commit()
            logger.info("✓ Migration: added is_walkin column to customer table")
        else:
            logger.debug("is_walkin column already exists — no migration needed")
    except Exception as exc:
        logger.warning("Could not verify/migrate is_walkin column: %s", exc)


def _insert_customers(session: Session):
    """
    Insert the Walk-in Customer placeholder and 15 sample UK customers.

    Walk-in Customer:
        is_walkin=True — all sale transactions that have no customer explicitly
        assigned will be linked to this record during document finalisation.

    Sample customers:
        Realistic United Kingdom residents with varied names, addresses and
        contact details used for development and demonstration purposes.
    """
    # Ensure the is_walkin column exists (adds it via ALTER TABLE on legacy DBs)
    _migrate_is_walkin_column(session)

    existing = session.query(Customer).first()
    if existing:
        logger.warning("✓ Customers already exist, skipping insertion")
        return

    customers = [
        # ------------------------------------------------------------------ #
        #  Walk-in Customer  (must be first — index 0)                        #
        # ------------------------------------------------------------------ #
        Customer(
            name="Walk-in",
            last_name="Customer",
            description="Default placeholder for anonymous / unassigned transactions",
            is_walkin=True,
            is_active=True,
            registration_source="POS",
        ),

        # ------------------------------------------------------------------ #
        #  Sample UK Customers                                                 #
        # ------------------------------------------------------------------ #
        Customer(
            name="James",
            last_name="Thornton",
            address_line_1="14 Elm Street",
            address_line_2="Kensington",
            address_line_3="London",
            zip_code="W8 4LZ",
            email_address="james.thornton@email.co.uk",
            phone_number="+44 20 7946 0101",
            date_of_birth=date(1985, 3, 12),
            gender="MALE",
            national_id="TN123456A",
            tax_id="GB123456789",
            registration_source="POS",
            marketing_consent=True,
            sms_consent=True,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Sophie",
            last_name="Wentworth",
            address_line_1="7 Blossom Lane",
            address_line_2="Clifton",
            address_line_3="Bristol",
            zip_code="BS8 2HQ",
            email_address="sophie.wentworth@email.co.uk",
            phone_number="+44 117 496 0202",
            date_of_birth=date(1990, 7, 24),
            gender="FEMALE",
            national_id="WS654321B",
            registration_source="WEBSITE",
            marketing_consent=True,
            sms_consent=False,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Oliver",
            last_name="Blackwood",
            address_line_1="32 Victoria Road",
            address_line_2="Headingley",
            address_line_3="Leeds",
            zip_code="LS6 1DS",
            email_address="oliver.blackwood@mail.co.uk",
            phone_number="+44 113 496 0303",
            date_of_birth=date(1978, 11, 5),
            gender="MALE",
            national_id="BL987654C",
            tax_id="GB987654321",
            registration_source="POS",
            marketing_consent=False,
            sms_consent=False,
            email_consent=False,
            is_active=True,
        ),
        Customer(
            name="Charlotte",
            last_name="Pemberton",
            address_line_1="5 Maple Avenue",
            address_line_2="Didsbury",
            address_line_3="Manchester",
            zip_code="M20 6RJ",
            email_address="charlotte.pemberton@webmail.co.uk",
            phone_number="+44 161 496 0404",
            date_of_birth=date(1995, 1, 30),
            gender="FEMALE",
            national_id="PE246810D",
            registration_source="MOBILE_APP",
            marketing_consent=True,
            sms_consent=True,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Harry",
            last_name="Aldridge",
            address_line_1="22 Oakwood Close",
            address_line_2="Jesmond",
            address_line_3="Newcastle upon Tyne",
            zip_code="NE2 1TF",
            email_address="harry.aldridge@inbox.co.uk",
            phone_number="+44 191 496 0505",
            date_of_birth=date(1982, 9, 18),
            gender="MALE",
            national_id="AL135790E",
            registration_source="POS",
            marketing_consent=True,
            sms_consent=False,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Emily",
            last_name="Forsythe",
            address_line_1="9 Roseberry Street",
            address_line_2="Morningside",
            address_line_3="Edinburgh",
            zip_code="EH10 4LN",
            email_address="emily.forsythe@scottishmail.co.uk",
            phone_number="+44 131 496 0606",
            date_of_birth=date(1988, 6, 14),
            gender="FEMALE",
            national_id="FO357924F",
            registration_source="REFERRAL",
            marketing_consent=True,
            sms_consent=True,
            email_consent=False,
            is_active=True,
        ),
        Customer(
            name="George",
            last_name="Hastings",
            address_line_1="18 Chandler's Way",
            address_line_2="Trumpington",
            address_line_3="Cambridge",
            zip_code="CB2 9AB",
            email_address="george.hastings@cammail.co.uk",
            phone_number="+44 1223 496 0707",
            date_of_birth=date(1975, 4, 22),
            gender="MALE",
            national_id="HA468024G",
            tax_id="GB468024111",
            registration_source="POS",
            marketing_consent=False,
            sms_consent=False,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Isabella",
            last_name="Stanhope",
            address_line_1="3 Lavender Gardens",
            address_line_2="Hove",
            address_line_3="East Sussex",
            zip_code="BN3 7PL",
            email_address="isabella.stanhope@seamail.co.uk",
            phone_number="+44 1273 496 0808",
            date_of_birth=date(1993, 12, 8),
            gender="FEMALE",
            national_id="ST579135H",
            registration_source="SOCIAL_MEDIA",
            marketing_consent=True,
            sms_consent=True,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="William",
            last_name="Carrington",
            address_line_1="47 Brunswick Square",
            address_line_2="Clifton",
            address_line_3="Bristol",
            zip_code="BS2 8EZ",
            email_address="william.carrington@bristolpost.co.uk",
            phone_number="+44 117 496 0909",
            date_of_birth=date(1970, 8, 31),
            gender="MALE",
            national_id="CA680246I",
            tax_id="GB680246222",
            registration_source="POS",
            marketing_consent=False,
            sms_consent=True,
            email_consent=False,
            is_active=True,
        ),
        Customer(
            name="Amelia",
            last_name="Blackstone",
            address_line_1="11 Chestnut Grove",
            address_line_2="Balham",
            address_line_3="London",
            zip_code="SW12 8JT",
            email_address="amelia.blackstone@londonmail.co.uk",
            phone_number="+44 20 7946 1010",
            date_of_birth=date(1997, 2, 3),
            gender="FEMALE",
            national_id="BS791357J",
            registration_source="MOBILE_APP",
            marketing_consent=True,
            sms_consent=True,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Thomas",
            last_name="Whitfield",
            address_line_1="66 Acacia Avenue",
            address_line_2="Harborne",
            address_line_3="Birmingham",
            zip_code="B17 9NP",
            email_address="thomas.whitfield@midmail.co.uk",
            phone_number="+44 121 496 1111",
            date_of_birth=date(1983, 5, 27),
            gender="MALE",
            national_id="WH802468K",
            registration_source="POS",
            marketing_consent=True,
            sms_consent=False,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Grace",
            last_name="Dunmore",
            address_line_1="28 Willow Walk",
            address_line_2="Witney",
            address_line_3="Oxfordshire",
            zip_code="OX28 6QR",
            email_address="grace.dunmore@oxmail.co.uk",
            phone_number="+44 1993 496 1212",
            date_of_birth=date(1991, 10, 16),
            gender="FEMALE",
            national_id="DU913579L",
            registration_source="WEBSITE",
            marketing_consent=False,
            sms_consent=False,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Edward",
            last_name="Kingsley",
            address_line_1="5 Orchard Road",
            address_line_2="Otley",
            address_line_3="West Yorkshire",
            zip_code="LS21 1BG",
            email_address="edward.kingsley@yorkmail.co.uk",
            phone_number="+44 1943 496 1313",
            date_of_birth=date(1968, 7, 9),
            gender="MALE",
            national_id="KI024680M",
            tax_id="GB024680333",
            registration_source="POS",
            marketing_consent=True,
            sms_consent=True,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Lucy",
            last_name="Davenport",
            address_line_1="13 Hawthorn Crescent",
            address_line_2="Sherwood",
            address_line_3="Nottingham",
            zip_code="NG5 3FH",
            email_address="lucy.davenport@nottsmail.co.uk",
            phone_number="+44 115 496 1414",
            date_of_birth=date(1986, 3, 20),
            gender="FEMALE",
            national_id="DA135791N",
            registration_source="REFERRAL",
            marketing_consent=True,
            sms_consent=False,
            email_consent=True,
            is_active=True,
        ),
        Customer(
            name="Arthur",
            last_name="Strickland",
            address_line_1="8 Harbour View",
            address_line_2="Portishead",
            address_line_3="North Somerset",
            zip_code="BS20 7DG",
            email_address="arthur.strickland@somerset.co.uk",
            phone_number="+44 1275 496 1515",
            date_of_birth=date(1979, 12, 1),
            gender="MALE",
            national_id="ST246802O",
            registration_source="POS",
            marketing_consent=False,
            sms_consent=True,
            email_consent=False,
            is_active=True,
        ),
    ]

    try:
        for customer in customers:
            session.add(customer)
        session.commit()
        logger.info("✓ Inserted %s customers (%s walk-in + %s sample)",
                    len(customers), 1, len(customers) - 1)
    except Exception as e:
        session.rollback()
        logger.error("✗ Error inserting customers: %s", e)
        raise


def seed_customers_now():
    """
    Standalone helper — insert customers into an **existing** database that was
    initialised before the Customer Management module was added.

    Call once from a Python shell or a one-off migration script::

        from data_layer.db_init_data.customer import seed_customers_now
        seed_customers_now()
    """
    from data_layer.engine import Engine
    engine = Engine()
    with engine.get_session() as session:
        _insert_customers(session)

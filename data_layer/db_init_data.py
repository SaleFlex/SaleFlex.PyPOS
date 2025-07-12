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

from data_layer.model import (
    Cashier, Customer, Store, Vat, ProductUnit, ProductManufacturer,
    DepartmentMainGroup, DepartmentSubGroup, TransactionDocumentType,
    TransactionSequence, ProductBarcodeMask, Country, City, District,
    Currency
)
from data_layer.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


def insert_initial_data(engine: Engine):
    """
    Inserts initial data (only if tables are empty)
    """
    try:
        with engine.get_session() as session:
            # Insert admin cashier
            admin_cashier = _insert_admin_cashier(session)
            
            # Insert default store
            _insert_default_store(session)
            
            # Insert countries
            _insert_countries(session)
            
            # Insert cities
            _insert_cities(session)
            
            # Insert districts
            _insert_districts(session)
            
            # Insert currencies
            _insert_currencies(session)
            
            # Insert VAT rates
            _insert_vat_rates(session, admin_cashier.id)
            
            # Insert product units
            _insert_product_units(session, admin_cashier.id)
            
            # Insert product manufacturers
            _insert_product_manufacturers(session)
            
            # Insert department groups
            _insert_department_groups(session, admin_cashier.id)
            
            # Insert transaction document types
            _insert_transaction_document_types(session)
            
            # Insert transaction sequences
            _insert_transaction_sequences(session, admin_cashier.id)
            
            # Insert product barcode masks
            _insert_product_barcode_masks(session, admin_cashier.id)
    
    except SQLAlchemyError as e:
        print(f"✗ Initial data insertion error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


def _insert_admin_cashier(session) -> Cashier:
    """Insert admin user if not exists"""
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
        print("✓ Admin user added")
        return admin_cashier
    else:
        return admin_exists


def _insert_default_store(session):
    """Insert default store if not exists"""
    store_exists = session.query(Store).first()
    if not store_exists:
        default_store = Store(
            name="Main Store",
            brand_name="SaleFlex",
            company_name="SaleFlex PyPOS",
            web_page_url="https://saleflex.com",
            description="Default store"
        )
        session.add(default_store)
        print("✓ Default store added")


def _insert_countries(session):
    """Insert countries if not exists"""
    country_exists = session.query(Country).first()
    if not country_exists:
        countries = [
            {"name": "Afghanistan", "code": "AF", "short_name": "AFG", "numeric_code": 4},
            {"name": "Albania", "code": "AL", "short_name": "ALB", "numeric_code": 8},
            {"name": "Algeria", "code": "DZ", "short_name": "DZA", "numeric_code": 12},
            {"name": "Andorra", "code": "AD", "short_name": "AND", "numeric_code": 20},
            {"name": "Angola", "code": "AO", "short_name": "AGO", "numeric_code": 24},
            {"name": "Argentina", "code": "AR", "short_name": "ARG", "numeric_code": 32},
            {"name": "Armenia", "code": "AM", "short_name": "ARM", "numeric_code": 51},
            {"name": "Australia", "code": "AU", "short_name": "AUS", "numeric_code": 36},
            {"name": "Austria", "code": "AT", "short_name": "AUT", "numeric_code": 40},
            {"name": "Azerbaijan", "code": "AZ", "short_name": "AZE", "numeric_code": 31},
            {"name": "Bahamas", "code": "BS", "short_name": "BHS", "numeric_code": 44},
            {"name": "Bahrain", "code": "BH", "short_name": "BHR", "numeric_code": 48},
            {"name": "Bangladesh", "code": "BD", "short_name": "BGD", "numeric_code": 50},
            {"name": "Barbados", "code": "BB", "short_name": "BRB", "numeric_code": 52},
            {"name": "Belarus", "code": "BY", "short_name": "BLR", "numeric_code": 112},
            {"name": "Belgium", "code": "BE", "short_name": "BEL", "numeric_code": 56},
            {"name": "Belize", "code": "BZ", "short_name": "BLZ", "numeric_code": 84},
            {"name": "Benin", "code": "BJ", "short_name": "BEN", "numeric_code": 204},
            {"name": "Bhutan", "code": "BT", "short_name": "BTN", "numeric_code": 64},
            {"name": "Bolivia", "code": "BO", "short_name": "BOL", "numeric_code": 68},
            {"name": "Bosnia and Herzegovina", "code": "BA", "short_name": "BIH", "numeric_code": 70},
            {"name": "Botswana", "code": "BW", "short_name": "BWA", "numeric_code": 72},
            {"name": "Brazil", "code": "BR", "short_name": "BRA", "numeric_code": 76},
            {"name": "Brunei", "code": "BN", "short_name": "BRN", "numeric_code": 96},
            {"name": "Bulgaria", "code": "BG", "short_name": "BGR", "numeric_code": 100},
            {"name": "Burkina Faso", "code": "BF", "short_name": "BFA", "numeric_code": 854},
            {"name": "Burundi", "code": "BI", "short_name": "BDI", "numeric_code": 108},
            {"name": "Cabo Verde", "code": "CV", "short_name": "CPV", "numeric_code": 132},
            {"name": "Cambodia", "code": "KH", "short_name": "KHM", "numeric_code": 116},
            {"name": "Cameroon", "code": "CM", "short_name": "CMR", "numeric_code": 120},
            {"name": "Canada", "code": "CA", "short_name": "CAN", "numeric_code": 124},
            {"name": "Central African Republic", "code": "CF", "short_name": "CAF", "numeric_code": 140},
            {"name": "Chad", "code": "TD", "short_name": "TCD", "numeric_code": 148},
            {"name": "Chile", "code": "CL", "short_name": "CHL", "numeric_code": 152},
            {"name": "China", "code": "CN", "short_name": "CHN", "numeric_code": 156},
            {"name": "Colombia", "code": "CO", "short_name": "COL", "numeric_code": 170},
            {"name": "Comoros", "code": "KM", "short_name": "COM", "numeric_code": 174},
            {"name": "Congo, Democratic Republic of the", "code": "CD", "short_name": "COD", "numeric_code": 180},
            {"name": "Congo, Republic of the", "code": "CG", "short_name": "COG", "numeric_code": 178},
            {"name": "Costa Rica", "code": "CR", "short_name": "CRI", "numeric_code": 188},
            {"name": "Croatia", "code": "HR", "short_name": "HRV", "numeric_code": 191},
            {"name": "Cuba", "code": "CU", "short_name": "CUB", "numeric_code": 192},
            {"name": "Cyprus", "code": "CY", "short_name": "CYP", "numeric_code": 196},
            {"name": "Czech Republic", "code": "CZ", "short_name": "CZE", "numeric_code": 203},
            {"name": "Denmark", "code": "DK", "short_name": "DNK", "numeric_code": 208},
            {"name": "Djibouti", "code": "DJ", "short_name": "DJI", "numeric_code": 262},
            {"name": "Dominica", "code": "DM", "short_name": "DMA", "numeric_code": 212},
            {"name": "Dominican Republic", "code": "DO", "short_name": "DOM", "numeric_code": 214},
            {"name": "Ecuador", "code": "EC", "short_name": "ECU", "numeric_code": 218},
            {"name": "Egypt", "code": "EG", "short_name": "EGY", "numeric_code": 818},
            {"name": "El Salvador", "code": "SV", "short_name": "SLV", "numeric_code": 222},
            {"name": "Equatorial Guinea", "code": "GQ", "short_name": "GNQ", "numeric_code": 226},
            {"name": "Eritrea", "code": "ER", "short_name": "ERI", "numeric_code": 232},
            {"name": "Estonia", "code": "EE", "short_name": "EST", "numeric_code": 233},
            {"name": "Eswatini", "code": "SZ", "short_name": "SWZ", "numeric_code": 748},
            {"name": "Ethiopia", "code": "ET", "short_name": "ETH", "numeric_code": 231},
            {"name": "Fiji", "code": "FJ", "short_name": "FJI", "numeric_code": 242},
            {"name": "Finland", "code": "FI", "short_name": "FIN", "numeric_code": 246},
            {"name": "France", "code": "FR", "short_name": "FRA", "numeric_code": 250},
            {"name": "Gabon", "code": "GA", "short_name": "GAB", "numeric_code": 266},
            {"name": "Gambia", "code": "GM", "short_name": "GMB", "numeric_code": 270},
            {"name": "Georgia", "code": "GE", "short_name": "GEO", "numeric_code": 268},
            {"name": "Germany", "code": "DE", "short_name": "DEU", "numeric_code": 276},
            {"name": "Ghana", "code": "GH", "short_name": "GHA", "numeric_code": 288},
            {"name": "Greece", "code": "GR", "short_name": "GRC", "numeric_code": 300},
            {"name": "Grenada", "code": "GD", "short_name": "GRD", "numeric_code": 308},
            {"name": "Guatemala", "code": "GT", "short_name": "GTM", "numeric_code": 320},
            {"name": "Guinea", "code": "GN", "short_name": "GIN", "numeric_code": 324},
            {"name": "Guinea-Bissau", "code": "GW", "short_name": "GNB", "numeric_code": 624},
            {"name": "Guyana", "code": "GY", "short_name": "GUY", "numeric_code": 328},
            {"name": "Haiti", "code": "HT", "short_name": "HTI", "numeric_code": 332},
            {"name": "Honduras", "code": "HN", "short_name": "HND", "numeric_code": 340},
            {"name": "Hungary", "code": "HU", "short_name": "HUN", "numeric_code": 348},
            {"name": "Iceland", "code": "IS", "short_name": "ISL", "numeric_code": 352},
            {"name": "India", "code": "IN", "short_name": "IND", "numeric_code": 356},
            {"name": "Indonesia", "code": "ID", "short_name": "IDN", "numeric_code": 360},
            {"name": "Iran", "code": "IR", "short_name": "IRN", "numeric_code": 364},
            {"name": "Iraq", "code": "IQ", "short_name": "IRQ", "numeric_code": 368},
            {"name": "Ireland", "code": "IE", "short_name": "IRL", "numeric_code": 372},
            {"name": "Israel", "code": "IL", "short_name": "ISR", "numeric_code": 376},
            {"name": "Italy", "code": "IT", "short_name": "ITA", "numeric_code": 380},
            {"name": "Jamaica", "code": "JM", "short_name": "JAM", "numeric_code": 388},
            {"name": "Japan", "code": "JP", "short_name": "JPN", "numeric_code": 392},
            {"name": "Jordan", "code": "JO", "short_name": "JOR", "numeric_code": 400},
            {"name": "Kazakhstan", "code": "KZ", "short_name": "KAZ", "numeric_code": 398},
            {"name": "Kenya", "code": "KE", "short_name": "KEN", "numeric_code": 404},
            {"name": "Kiribati", "code": "KI", "short_name": "KIR", "numeric_code": 296},
            {"name": "Korea, North", "code": "KP", "short_name": "PRK", "numeric_code": 408},
            {"name": "Korea, South", "code": "KR", "short_name": "KOR", "numeric_code": 410},
            {"name": "Kuwait", "code": "KW", "short_name": "KWT", "numeric_code": 414},
            {"name": "Kyrgyzstan", "code": "KG", "short_name": "KGZ", "numeric_code": 417},
            {"name": "Laos", "code": "LA", "short_name": "LAO", "numeric_code": 418},
            {"name": "Latvia", "code": "LV", "short_name": "LVA", "numeric_code": 428},
            {"name": "Lebanon", "code": "LB", "short_name": "LBN", "numeric_code": 422},
            {"name": "Lesotho", "code": "LS", "short_name": "LSO", "numeric_code": 426},
            {"name": "Liberia", "code": "LR", "short_name": "LBR", "numeric_code": 430},
            {"name": "Libya", "code": "LY", "short_name": "LBY", "numeric_code": 434},
            {"name": "Liechtenstein", "code": "LI", "short_name": "LIE", "numeric_code": 438},
            {"name": "Lithuania", "code": "LT", "short_name": "LTU", "numeric_code": 440},
            {"name": "Luxembourg", "code": "LU", "short_name": "LUX", "numeric_code": 442},
            {"name": "Madagascar", "code": "MG", "short_name": "MDG", "numeric_code": 450},
            {"name": "Malawi", "code": "MW", "short_name": "MWI", "numeric_code": 454},
            {"name": "Malaysia", "code": "MY", "short_name": "MYS", "numeric_code": 458},
            {"name": "Maldives", "code": "MV", "short_name": "MDV", "numeric_code": 462},
            {"name": "Mali", "code": "ML", "short_name": "MLI", "numeric_code": 466},
            {"name": "Malta", "code": "MT", "short_name": "MLT", "numeric_code": 470},
            {"name": "Marshall Islands", "code": "MH", "short_name": "MHL", "numeric_code": 584},
            {"name": "Mauritania", "code": "MR", "short_name": "MRT", "numeric_code": 478},
            {"name": "Mauritius", "code": "MU", "short_name": "MUS", "numeric_code": 480},
            {"name": "Mexico", "code": "MX", "short_name": "MEX", "numeric_code": 484},
            {"name": "Micronesia", "code": "FM", "short_name": "FSM", "numeric_code": 583},
            {"name": "Moldova", "code": "MD", "short_name": "MDA", "numeric_code": 498},
            {"name": "Monaco", "code": "MC", "short_name": "MCO", "numeric_code": 492},
            {"name": "Mongolia", "code": "MN", "short_name": "MNG", "numeric_code": 496},
            {"name": "Montenegro", "code": "ME", "short_name": "MNE", "numeric_code": 499},
            {"name": "Morocco", "code": "MA", "short_name": "MAR", "numeric_code": 504},
            {"name": "Mozambique", "code": "MZ", "short_name": "MOZ", "numeric_code": 508},
            {"name": "Myanmar", "code": "MM", "short_name": "MMR", "numeric_code": 104},
            {"name": "Namibia", "code": "NA", "short_name": "NAM", "numeric_code": 516},
            {"name": "Nauru", "code": "NR", "short_name": "NRU", "numeric_code": 520},
            {"name": "Nepal", "code": "NP", "short_name": "NPL", "numeric_code": 524},
            {"name": "Netherlands", "code": "NL", "short_name": "NLD", "numeric_code": 528},
            {"name": "New Zealand", "code": "NZ", "short_name": "NZL", "numeric_code": 554},
            {"name": "Nicaragua", "code": "NI", "short_name": "NIC", "numeric_code": 558},
            {"name": "Niger", "code": "NE", "short_name": "NER", "numeric_code": 562},
            {"name": "Nigeria", "code": "NG", "short_name": "NGA", "numeric_code": 566},
            {"name": "North Macedonia", "code": "MK", "short_name": "MKD", "numeric_code": 807},
            {"name": "Norway", "code": "NO", "short_name": "NOR", "numeric_code": 578},
            {"name": "Oman", "code": "OM", "short_name": "OMN", "numeric_code": 512},
            {"name": "Pakistan", "code": "PK", "short_name": "PAK", "numeric_code": 586},
            {"name": "Palau", "code": "PW", "short_name": "PLW", "numeric_code": 585},
            {"name": "Panama", "code": "PA", "short_name": "PAN", "numeric_code": 591},
            {"name": "Papua New Guinea", "code": "PG", "short_name": "PNG", "numeric_code": 598},
            {"name": "Paraguay", "code": "PY", "short_name": "PRY", "numeric_code": 600},
            {"name": "Peru", "code": "PE", "short_name": "PER", "numeric_code": 604},
            {"name": "Philippines", "code": "PH", "short_name": "PHL", "numeric_code": 608},
            {"name": "Poland", "code": "PL", "short_name": "POL", "numeric_code": 616},
            {"name": "Portugal", "code": "PT", "short_name": "PRT", "numeric_code": 620},
            {"name": "Qatar", "code": "QA", "short_name": "QAT", "numeric_code": 634},
            {"name": "Romania", "code": "RO", "short_name": "ROU", "numeric_code": 642},
            {"name": "Russia", "code": "RU", "short_name": "RUS", "numeric_code": 643},
            {"name": "Rwanda", "code": "RW", "short_name": "RWA", "numeric_code": 646},
            {"name": "Saint Kitts and Nevis", "code": "KN", "short_name": "KNA", "numeric_code": 659},
            {"name": "Saint Lucia", "code": "LC", "short_name": "LCA", "numeric_code": 662},
            {"name": "Saint Vincent and the Grenadines", "code": "VC", "short_name": "VCT", "numeric_code": 670},
            {"name": "Samoa", "code": "WS", "short_name": "WSM", "numeric_code": 882},
            {"name": "San Marino", "code": "SM", "short_name": "SMR", "numeric_code": 674},
            {"name": "Sao Tome and Principe", "code": "ST", "short_name": "STP", "numeric_code": 678},
            {"name": "Saudi Arabia", "code": "SA", "short_name": "SAU", "numeric_code": 682},
            {"name": "Senegal", "code": "SN", "short_name": "SEN", "numeric_code": 686},
            {"name": "Serbia", "code": "RS", "short_name": "SRB", "numeric_code": 688},
            {"name": "Seychelles", "code": "SC", "short_name": "SYC", "numeric_code": 690},
            {"name": "Sierra Leone", "code": "SL", "short_name": "SLE", "numeric_code": 694},
            {"name": "Singapore", "code": "SG", "short_name": "SGP", "numeric_code": 702},
            {"name": "Slovakia", "code": "SK", "short_name": "SVK", "numeric_code": 703},
            {"name": "Slovenia", "code": "SI", "short_name": "SVN", "numeric_code": 705},
            {"name": "Solomon Islands", "code": "SB", "short_name": "SLB", "numeric_code": 90},
            {"name": "Somalia", "code": "SO", "short_name": "SOM", "numeric_code": 706},
            {"name": "South Africa", "code": "ZA", "short_name": "ZAF", "numeric_code": 710},
            {"name": "South Sudan", "code": "SS", "short_name": "SSD", "numeric_code": 728},
            {"name": "Spain", "code": "ES", "short_name": "ESP", "numeric_code": 724},
            {"name": "Sri Lanka", "code": "LK", "short_name": "LKA", "numeric_code": 144},
            {"name": "Sudan", "code": "SD", "short_name": "SDN", "numeric_code": 729},
            {"name": "Suriname", "code": "SR", "short_name": "SUR", "numeric_code": 740},
            {"name": "Sweden", "code": "SE", "short_name": "SWE", "numeric_code": 752},
            {"name": "Switzerland", "code": "CH", "short_name": "CHE", "numeric_code": 756},
            {"name": "Syria", "code": "SY", "short_name": "SYR", "numeric_code": 760},
            {"name": "Taiwan", "code": "TW", "short_name": "TWN", "numeric_code": 158},
            {"name": "Tajikistan", "code": "TJ", "short_name": "TJK", "numeric_code": 762},
            {"name": "Tanzania", "code": "TZ", "short_name": "TZA", "numeric_code": 834},
            {"name": "Thailand", "code": "TH", "short_name": "THA", "numeric_code": 764},
            {"name": "Timor-Leste", "code": "TL", "short_name": "TLS", "numeric_code": 626},
            {"name": "Togo", "code": "TG", "short_name": "TGO", "numeric_code": 768},
            {"name": "Tonga", "code": "TO", "short_name": "TON", "numeric_code": 776},
            {"name": "Trinidad and Tobago", "code": "TT", "short_name": "TTO", "numeric_code": 780},
            {"name": "Tunisia", "code": "TN", "short_name": "TUN", "numeric_code": 788},
            {"name": "Turkey", "code": "TR", "short_name": "TUR", "numeric_code": 792},
            {"name": "Turkmenistan", "code": "TM", "short_name": "TKM", "numeric_code": 795},
            {"name": "Tuvalu", "code": "TV", "short_name": "TUV", "numeric_code": 798},
            {"name": "Uganda", "code": "UG", "short_name": "UGA", "numeric_code": 800},
            {"name": "Ukraine", "code": "UA", "short_name": "UKR", "numeric_code": 804},
            {"name": "United Arab Emirates", "code": "AE", "short_name": "ARE", "numeric_code": 784},
            {"name": "United Kingdom", "code": "GB", "short_name": "GBR", "numeric_code": 826},
            {"name": "United States", "code": "US", "short_name": "USA", "numeric_code": 840},
            {"name": "Uruguay", "code": "UY", "short_name": "URY", "numeric_code": 858},
            {"name": "Uzbekistan", "code": "UZ", "short_name": "UZB", "numeric_code": 860},
            {"name": "Vanuatu", "code": "VU", "short_name": "VUT", "numeric_code": 548},
            {"name": "Vatican City", "code": "VA", "short_name": "VAT", "numeric_code": 336},
            {"name": "Venezuela", "code": "VE", "short_name": "VEN", "numeric_code": 862},
            {"name": "Vietnam", "code": "VN", "short_name": "VNM", "numeric_code": 704},
            {"name": "Yemen", "code": "YE", "short_name": "YEM", "numeric_code": 887},
            {"name": "Zambia", "code": "ZM", "short_name": "ZMB", "numeric_code": 894},
            {"name": "Zimbabwe", "code": "ZW", "short_name": "ZWE", "numeric_code": 716}
        ]
        
        for country_data in countries:
            country = Country(
                name=country_data["name"],
                code=country_data["code"],
                short_name=country_data["short_name"],
                numeric_code=country_data["numeric_code"]
            )
            session.add(country)
        
        print("✓ Countries added (195 countries)")


def _insert_cities(session):
    """Insert UK cities if not exists"""
    city_exists = session.query(City).first()
    if not city_exists:
        # First, get the UK country ID
        uk_country = session.query(Country).filter_by(code="GB").first()
        if not uk_country:
            print("⚠ UK country not found, skipping city insertion")
            return
        
        cities = [
            {"name": "Bath", "code": "GB-BTH", "short_name": "BTH", "numeric_code": 1},
            {"name": "Birmingham", "code": "GB-BIR", "short_name": "BHM", "numeric_code": 2},
            {"name": "Bradford", "code": "GB-BRD", "short_name": "BRD", "numeric_code": 3},
            {"name": "Brighton & Hove", "code": "GB-BHV", "short_name": "BHV", "numeric_code": 4},
            {"name": "Bristol", "code": "GB-BST", "short_name": "BRS", "numeric_code": 5},
            {"name": "Cambridge", "code": "GB-CAM", "short_name": "CAM", "numeric_code": 6},
            {"name": "Canterbury", "code": "GB-CNT", "short_name": "CNT", "numeric_code": 7},
            {"name": "Carlisle", "code": "GB-CAR", "short_name": "CAR", "numeric_code": 8},
            {"name": "Chelmsford", "code": "GB-CHE", "short_name": "CHE", "numeric_code": 9},
            {"name": "Chester", "code": "GB-CHS", "short_name": "CHS", "numeric_code": 10},
            {"name": "Chichester", "code": "GB-CHI", "short_name": "CHI", "numeric_code": 11},
            {"name": "Colchester", "code": "GB-COL", "short_name": "COL", "numeric_code": 12},
            {"name": "Coventry", "code": "GB-COV", "short_name": "COV", "numeric_code": 13},
            {"name": "Derby", "code": "GB-DER", "short_name": "DER", "numeric_code": 14},
            {"name": "Doncaster", "code": "GB-DON", "short_name": "DON", "numeric_code": 15},
            {"name": "Durham", "code": "GB-DUR", "short_name": "DUR", "numeric_code": 16},
            {"name": "Ely", "code": "GB-ELY", "short_name": "ELY", "numeric_code": 17},
            {"name": "Exeter", "code": "GB-EXE", "short_name": "EXE", "numeric_code": 18},
            {"name": "Gloucester", "code": "GB-GLO", "short_name": "GLO", "numeric_code": 19},
            {"name": "Hereford", "code": "GB-HER", "short_name": "HER", "numeric_code": 20},
            {"name": "Kingston upon Hull", "code": "GB-HUL", "short_name": "HUL", "numeric_code": 21},
            {"name": "Lancaster", "code": "GB-LAN", "short_name": "LAN", "numeric_code": 22},
            {"name": "Leeds", "code": "GB-LDS", "short_name": "LDS", "numeric_code": 23},
            {"name": "Leicester", "code": "GB-LEI", "short_name": "LEI", "numeric_code": 24},
            {"name": "Lichfield", "code": "GB-LIC", "short_name": "LIC", "numeric_code": 25},
            {"name": "Lincoln", "code": "GB-LIN", "short_name": "LIN", "numeric_code": 26},
            {"name": "Liverpool", "code": "GB-LIV", "short_name": "LIV", "numeric_code": 27},
            {"name": "London", "code": "GB-LND", "short_name": "LDN", "numeric_code": 28},
            {"name": "Manchester", "code": "GB-MAN", "short_name": "MAN", "numeric_code": 29},
            {"name": "Milton Keynes", "code": "GB-MKN", "short_name": "MKN", "numeric_code": 30},
            {"name": "Newcastle upon Tyne", "code": "GB-NET", "short_name": "NCL", "numeric_code": 31},
            {"name": "Norwich", "code": "GB-NOR", "short_name": "NOR", "numeric_code": 32},
            {"name": "Nottingham", "code": "GB-NGM", "short_name": "NTG", "numeric_code": 33},
            {"name": "Oxford", "code": "GB-OXF", "short_name": "OXF", "numeric_code": 34},
            {"name": "Peterborough", "code": "GB-PTR", "short_name": "PTR", "numeric_code": 35},
            {"name": "Plymouth", "code": "GB-PLY", "short_name": "PLY", "numeric_code": 36},
            {"name": "Portsmouth", "code": "GB-POR", "short_name": "POR", "numeric_code": 37},
            {"name": "Preston", "code": "GB-PRE", "short_name": "PRE", "numeric_code": 38},
            {"name": "Ripon", "code": "GB-RIP", "short_name": "RIP", "numeric_code": 39},
            {"name": "Salford", "code": "GB-SAL", "short_name": "SAL", "numeric_code": 40},
            {"name": "Salisbury", "code": "GB-SLB", "short_name": "SLB", "numeric_code": 41},
            {"name": "Sheffield", "code": "GB-SHF", "short_name": "SHF", "numeric_code": 42},
            {"name": "Southampton", "code": "GB-STH", "short_name": "SOU", "numeric_code": 43},
            {"name": "Stoke-on-Trent", "code": "GB-STK", "short_name": "STK", "numeric_code": 44},
            {"name": "Sunderland", "code": "GB-SUN", "short_name": "SUN", "numeric_code": 45},
            {"name": "Truro", "code": "GB-TRU", "short_name": "TRU", "numeric_code": 46},
            {"name": "Wakefield", "code": "GB-WAK", "short_name": "WAK", "numeric_code": 47},
            {"name": "Wells", "code": "GB-WEL", "short_name": "WEL", "numeric_code": 48},
            {"name": "Westminster", "code": "GB-WES", "short_name": "WES", "numeric_code": 49},
            {"name": "Winchester", "code": "GB-WIN", "short_name": "WIN", "numeric_code": 50},
            {"name": "Wolverhampton", "code": "GB-WOL", "short_name": "WOL", "numeric_code": 51},
            {"name": "Worcester", "code": "GB-WOR", "short_name": "WOR", "numeric_code": 52},
            {"name": "York", "code": "GB-YOR", "short_name": "YOR", "numeric_code": 53},
            # Scotland
            {"name": "Aberdeen", "code": "GB-ABD", "short_name": "ABD", "numeric_code": 54},
            {"name": "Dundee", "code": "GB-DUN", "short_name": "DUN", "numeric_code": 55},
            {"name": "Dunfermline", "code": "GB-DFL", "short_name": "DFL", "numeric_code": 56},
            {"name": "Edinburgh", "code": "GB-EDI", "short_name": "EDI", "numeric_code": 57},
            {"name": "Glasgow", "code": "GB-GLA", "short_name": "GLA", "numeric_code": 58},
            {"name": "Inverness", "code": "GB-INV", "short_name": "INV", "numeric_code": 59},
            {"name": "Perth", "code": "GB-PER", "short_name": "PER", "numeric_code": 60},
            {"name": "Stirling", "code": "GB-STI", "short_name": "STI", "numeric_code": 61},
            # Wales
            {"name": "Bangor (Wales)", "code": "GB-BAN", "short_name": "BAN", "numeric_code": 62},
            {"name": "Cardiff", "code": "GB-CDF", "short_name": "CDF", "numeric_code": 63},
            {"name": "Newport", "code": "GB-NEW", "short_name": "NEW", "numeric_code": 64},
            {"name": "St Asaph", "code": "GB-STA", "short_name": "STA", "numeric_code": 65},
            {"name": "St Davids", "code": "GB-STD", "short_name": "STD", "numeric_code": 66},
            {"name": "Swansea", "code": "GB-SWA", "short_name": "SWA", "numeric_code": 67},
            {"name": "Wrexham", "code": "GB-WRX", "short_name": "WRX", "numeric_code": 68},
            # Northern Ireland
            {"name": "Armagh", "code": "GB-ARM", "short_name": "ARM", "numeric_code": 69},
            {"name": "Bangor (Northern Ireland)", "code": "GB-BNI", "short_name": "BNI", "numeric_code": 70},
            {"name": "Belfast", "code": "GB-BEL", "short_name": "BEL", "numeric_code": 71},
            {"name": "Lisburn", "code": "GB-LIS", "short_name": "LIS", "numeric_code": 72},
            {"name": "Londonderry", "code": "GB-LDR", "short_name": "LDR", "numeric_code": 73},
            {"name": "Newry", "code": "GB-NWR", "short_name": "NWR", "numeric_code": 74}
        ]
        
        for city_data in cities:
            city = City(
                name=city_data["name"],
                code=city_data["code"],
                short_name=city_data["short_name"],
                numeric_code=city_data["numeric_code"],
                fk_country_id=uk_country.id
            )
            session.add(city)
        
        print("✓ UK cities added (74 cities)")


def _insert_vat_rates(session, admin_cashier_id: int):
    """Insert default VAT rates if not exists"""
    vat_exists = session.query(Vat).first()
    if not vat_exists:
        vat_rates = [
            {"name": "%0", "no": 1, "rate": 0, "description": "Zero VAT Rate (0%)"},
            {"name": "%5", "no": 2, "rate": 5, "description": "Reduced VAT Rate (5%)"},
            {"name": "%20", "no": 3, "rate": 20, "description": "Standard VAT Rate (20%)"}
        ]
        
        for vat_data in vat_rates:
            vat = Vat(
                name=vat_data["name"],
                no=vat_data["no"],
                rate=vat_data["rate"],
                description=vat_data["description"]
            )
            vat.fk_cashier_create_id = admin_cashier_id
            vat.fk_cashier_update_id = admin_cashier_id
            session.add(vat)
        print("✓ Default VAT rates added")


def _insert_product_units(session, admin_cashier_id: int):
    """Insert default product units if not exists"""
    unit_exists = session.query(ProductUnit).first()
    if not unit_exists:
        units = [
            {"code": "PCS", "name": "Pieces", "description": "Pieces unit"},
            {"code": "KG", "name": "Kilogram", "description": "Kilogram unit"},
            {"code": "GR", "name": "Gram", "description": "Gram unit"},
            {"code": "LT", "name": "Liter", "description": "Liter unit"},
            {"code": "M", "name": "Meter", "description": "Meter unit"},
            {"code": "M2", "name": "Square Meter", "description": "Square meter unit"},
            {"code": "PKT", "name": "Package", "description": "Package unit"}
        ]
        
        for unit_data in units:
            unit = ProductUnit(
                code=unit_data["code"],
                name=unit_data["name"],
                description=unit_data["description"]
            )
            unit.fk_cashier_create_id = admin_cashier_id
            unit.fk_cashier_update_id = admin_cashier_id
            session.add(unit)
        print("✓ Default product units added")


def _insert_product_manufacturers(session):
    """Insert default product manufacturers if not exists"""
    manufacturer_exists = session.query(ProductManufacturer).first()
    if not manufacturer_exists:
        default_manufacturer = ProductManufacturer(
            name="General Manufacturer",
            description="Default manufacturer for products without specific manufacturer"
        )
        session.add(default_manufacturer)
        print("✓ Default product manufacturer added")


def _insert_department_groups(session, admin_cashier_id: int):
    """Insert default department groups if not exists"""
    main_group_exists = session.query(DepartmentMainGroup).first()
    if not main_group_exists:
        # First get VAT IDs by their no values
        vat_0_percent = session.query(Vat).filter_by(no=1).first()  # %0 VAT
        vat_20_percent = session.query(Vat).filter_by(no=3).first()  # %20 VAT
        
        main_groups = [
            {
                "code": "1",
                "name": "FOOD",
                "description": "Food products department",
                "max_price": 100.0,
                "vat_id": vat_0_percent.id if vat_0_percent else None
            },
            {
                "code": "2", 
                "name": "TOBACCO",
                "description": "Tobacco products department",
                "max_price": 200.0,
                "vat_id": vat_20_percent.id if vat_20_percent else None
            },
            {
                "code": "3",
                "name": "INDIVIDUAL",
                "description": "Individual products department", 
                "max_price": 300.0,
                "vat_id": vat_20_percent.id if vat_20_percent else None
            }
        ]
        
        # Create main groups and store them for sub group creation
        created_main_groups = []
        for group_data in main_groups:
            main_group = DepartmentMainGroup(
                code=group_data["code"],
                name=group_data["name"],
                description=group_data["description"]
            )
            main_group.max_price = group_data["max_price"]
            main_group.fk_vat_id = group_data["vat_id"]
            main_group.fk_cashier_create_id = admin_cashier_id
            main_group.fk_cashier_update_id = admin_cashier_id
            session.add(main_group)
            session.flush()  # To get the ID
            created_main_groups.append(main_group)
        
        # Create sub groups for each main group
        _insert_department_sub_groups(session, admin_cashier_id, created_main_groups)
        
        print("✓ Default main groups added: FOOD, TOBACCO, INDIVIDUAL")
        print("✓ Default sub groups added")


def _insert_department_sub_groups(session, admin_cashier_id: int, main_groups):
    """Insert default department sub groups"""
    sub_groups_data = [
        # FOOD sub groups
        {"main_group_code": "1", "code": "101", "name": "FRESH FOOD", "description": "Fresh food products"},
        {"main_group_code": "1", "code": "102", "name": "CANNED FOOD", "description": "Canned and preserved food"},
        {"main_group_code": "1", "code": "103", "name": "BEVERAGES", "description": "Drinks and beverages"},
        
        # TOBACCO sub groups
        {"main_group_code": "2", "code": "201", "name": "CIGARETTES", "description": "Cigarette products"},
        {"main_group_code": "2", "code": "202", "name": "TOBACCO PRODUCTS", "description": "Other tobacco products"},
        
        # INDIVIDUAL sub groups
        {"main_group_code": "3", "code": "301", "name": "PERSONAL CARE", "description": "Personal care items"},
        {"main_group_code": "3", "code": "302", "name": "HOUSEHOLD ITEMS", "description": "Household products"},
        {"main_group_code": "3", "code": "303", "name": "ACCESSORIES", "description": "General accessories"}
    ]
    
    for sub_group_data in sub_groups_data:
        # Find the corresponding main group
        main_group = next((mg for mg in main_groups if mg.code == sub_group_data["main_group_code"]), None)
        if main_group:
            sub_group = DepartmentSubGroup(
                main_group_id=main_group.id,
                code=sub_group_data["code"],
                name=sub_group_data["name"],
                description=sub_group_data["description"]
            )
            sub_group.fk_cashier_create_id = admin_cashier_id
            sub_group.fk_cashier_update_id = admin_cashier_id
            session.add(sub_group)


def _insert_transaction_document_types(session):
    """Insert default transaction document types if not exists"""
    doc_type_exists = session.query(TransactionDocumentType).first()
    if not doc_type_exists:
        document_types = [
            {"no": 1, "name": "FISCAL_RECEIPT", "display_name": "Receipt", "description": "Fiscal Receipt"},
            {"no": 2, "name": "NONE_FISCAL_RECEIPT", "display_name": "Receipt", "description": "Non Fiscal Receipt"},
            {"no": 3, "name": "NONE_FISCAL_INVOICE", "display_name": "Invoice", "description": "Printed Invoice"},
            {"no": 4, "name": "NONE_FISCAL_E_INVOICE", "display_name": "E Invoice", "description": "Electronic Invoice"},
            {"no": 5, "name": "NONE_FISCAL_E_ARCHIVE_INVOICE", "display_name": "E Archive Invoice", "description": "Electronic Archive Invoice"},
            {"no": 6, "name": "NONE_FISCAL_DIPLOMATIC_RECEIPT", "display_name": "Diplomatic Invoice", "description": "Diplomatic Invoice"},
            {"no": 7, "name": "NONE_FISCAL_WAYBILL", "display_name": "Waybill", "description": "Waybill"},
            {"no": 8, "name": "NONE_FISCAL_DELIVERY_NOTE", "display_name": "Delivery Note", "description": "Delivery Note"},
            {"no": 9, "name": "NONE_FISCAL_CASH_OUT_FLOW", "display_name": "Cash Out flow", "description": "Cash Out flow"},
            {"no": 10, "name": "NONE_FISCAL_CASH_IN_FLOW", "display_name": "Cash In flow", "description": "Cash In flow"},
            {"no": 11, "name": "NONE_FISCAL_RETURN", "display_name": "Return", "description": "Return"},
            {"no": 12, "name": "NONE_FISCAL_SELF_BILLING_INVOICE", "display_name": "Self Billing Invoice", "description": "Self Billing Invoice"}
        ]
        
        for doc_type_data in document_types:
            doc_type = TransactionDocumentType(
                no=doc_type_data["no"],
                name=doc_type_data["name"],
                display_name=doc_type_data["display_name"],
                description=doc_type_data["description"]
            )
            session.add(doc_type)
        print("✓ Default transaction document types added")


def _insert_transaction_sequences(session, admin_cashier_id: int):
    """Insert default transaction sequences if not exists"""
    sequence_exists = session.query(TransactionSequence).first()
    if not sequence_exists:
        sequences = [
            {"name": "ReceiptNumber", "value": 1, "description": "Receipt sequence number"},
            {"name": "ZNumber", "value": 1, "description": "Z report sequence number"}
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


def _insert_product_barcode_masks(session, admin_cashier_id: int):
    """Insert default product barcode masks if not exists"""
    barcode_mask_exists = session.query(ProductBarcodeMask).first()
    if not barcode_mask_exists:
        weighed_goods_mask = ProductBarcodeMask()
        weighed_goods_mask.barcode_length = 19
        weighed_goods_mask.starting_digits = '1'
        weighed_goods_mask.code_started_at = 1  # 0-based index
        weighed_goods_mask.code_length = 6
        weighed_goods_mask.weight_started_at = 7
        weighed_goods_mask.weight_length = 6
        weighed_goods_mask.price_started_at = 13
        weighed_goods_mask.price_length = 6
        weighed_goods_mask.description = 'WEIGHED GOODS'
        weighed_goods_mask.fk_cashier_create_id = admin_cashier_id
        weighed_goods_mask.fk_cashier_update_id = admin_cashier_id
        
        session.add(weighed_goods_mask)
        print("✓ Default product barcode mask added: WEIGHED GOODS")


def _insert_districts(session):
    """Insert London districts if not exists"""
    district_exists = session.query(District).first()
    if not district_exists:
        # First, get the London city ID
        london_city = session.query(City).filter_by(code="GB-LND").first()
        if not london_city:
            print("⚠ London city not found, skipping district insertion")
            return
        
        districts = [
            {"name": "Camden", "code": "LDN-C", "short_name": "CAM", "numeric_code": 1},
            {"name": "Greenwich", "code": "LDN-G", "short_name": "GRN", "numeric_code": 2},
            {"name": "Hackney", "code": "LDN-H", "short_name": "HAC", "numeric_code": 3},
            {"name": "Hammersmith and Fulham", "code": "LDN-HAF", "short_name": "HAF", "numeric_code": 4},
            {"name": "Islington", "code": "LDN-I", "short_name": "ISL", "numeric_code": 5},
            {"name": "Kensington and Chelsea", "code": "LDN-KAC", "short_name": "KAC", "numeric_code": 6},
            {"name": "Lambeth", "code": "LDN-L", "short_name": "LAM", "numeric_code": 7},
            {"name": "Lewisham", "code": "LDN-LEW", "short_name": "LEW", "numeric_code": 8},
            {"name": "Southwark", "code": "LDN-S", "short_name": "SOW", "numeric_code": 9},
            {"name": "Tower Hamlets", "code": "LDN-TH", "short_name": "TH", "numeric_code": 10},
            {"name": "Wandsworth", "code": "LDN-W", "short_name": "WAN", "numeric_code": 11},
            {"name": "Westminster", "code": "LDN-WES", "short_name": "WES", "numeric_code": 12},
            {"name": "City of London", "code": "LDN-COL", "short_name": "COL", "numeric_code": 13},
            {"name": "Barking and Dagenham", "code": "LDN-BAD", "short_name": "BAD", "numeric_code": 14},
            {"name": "Barnet", "code": "LDN-BAR", "short_name": "BAR", "numeric_code": 15},
            {"name": "Bexley", "code": "LDN-BEX", "short_name": "BEX", "numeric_code": 16},
            {"name": "Brent", "code": "LDN-BRE", "short_name": "BRE", "numeric_code": 17},
            {"name": "Bromley", "code": "LDN-BRO", "short_name": "BRO", "numeric_code": 18},
            {"name": "Croydon", "code": "LDN-CRO", "short_name": "CRO", "numeric_code": 19},
            {"name": "Ealing", "code": "LDN-EAL", "short_name": "EAL", "numeric_code": 20},
            {"name": "Enfield", "code": "LDN-ENF", "short_name": "ENF", "numeric_code": 21},
            {"name": "Haringey", "code": "LDN-HAR", "short_name": "HAR", "numeric_code": 22},
            {"name": "Harrow", "code": "LDN-HRW", "short_name": "HRW", "numeric_code": 23},
            {"name": "Havering", "code": "LDN-HAV", "short_name": "HAV", "numeric_code": 24},
            {"name": "Hillingdon", "code": "LDN-HIL", "short_name": "HIL", "numeric_code": 25},
            {"name": "Hounslow", "code": "LDN-HOU", "short_name": "HOU", "numeric_code": 26},
            {"name": "Kingston upon Thames", "code": "LDN-KUT", "short_name": "KUT", "numeric_code": 27},
            {"name": "Merton", "code": "LDN-MER", "short_name": "MER", "numeric_code": 28},
            {"name": "Newham", "code": "LDN-NEW", "short_name": "NEW", "numeric_code": 29},
            {"name": "Redbridge", "code": "LDN-RED", "short_name": "RED", "numeric_code": 30},
            {"name": "Richmond upon Thames", "code": "LDN-RUT", "short_name": "RUT", "numeric_code": 31},
            {"name": "Sutton", "code": "LDN-SUT", "short_name": "SUT", "numeric_code": 32},
            {"name": "Waltham Forest", "code": "LDN-WF", "short_name": "WF", "numeric_code": 33}
        ]
        
        for district_data in districts:
            district = District(
                name=district_data["name"],
                code=district_data["code"],
                short_name=district_data["short_name"],
                numeric_code=district_data["numeric_code"],
                fk_city_id=london_city.id
            )
            session.add(district)
        
        print("✓ London districts added (33 districts)") 


def _insert_currencies(session):
    """Insert default currencies if not exists"""
    currency_exists = session.query(Currency).first()
    if not currency_exists:
        currencies = [
            {
                "no": 1,
                "name": "Argentine Peso",
                "currency_code": 32,
                "sign": "ARS",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1025.50
            },
            {
                "no": 2,
                "name": "Australian Dollar",
                "currency_code": 36,
                "sign": "AUD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 2.05
            },
            {
                "no": 3,
                "name": "Brazilian Real",
                "currency_code": 986,
                "sign": "BRL",
                "sign_direction": "LEFT",
                "currency_symbol": "R$",
                "rate": 7.85
            },
            {
                "no": 4,
                "name": "British Pound",
                "currency_code": 826,
                "sign": "GBP",
                "sign_direction": "LEFT",
                "currency_symbol": "£",
                "rate": 1.0
            },
            {
                "no": 5,
                "name": "Canadian Dollar",
                "currency_code": 124,
                "sign": "CAD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1.82
            },
            {
                "no": 6,
                "name": "Chilean Peso",
                "currency_code": 152,
                "sign": "CLP",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1245.80
            },
            {
                "no": 7,
                "name": "Chinese Yuan",
                "currency_code": 156,
                "sign": "CNY",
                "sign_direction": "LEFT",
                "currency_symbol": "¥",
                "rate": 9.46
            },
            {
                "no": 8,
                "name": "Colombian Peso",
                "currency_code": 170,
                "sign": "COP",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 5287.45
            },
            {
                "no": 9,
                "name": "Czech Koruna",
                "currency_code": 203,
                "sign": "CZK",
                "sign_direction": "LEFT",
                "currency_symbol": "Kč",
                "rate": 28.35
            },
            {
                "no": 10,
                "name": "Danish Krone",
                "currency_code": 208,
                "sign": "DKK",
                "sign_direction": "LEFT",
                "currency_symbol": "kr",
                "rate": 8.80
            },
            {
                "no": 11,
                "name": "Egyptian Pound",
                "currency_code": 818,
                "sign": "EGP",
                "sign_direction": "LEFT",
                "currency_symbol": "£",
                "rate": 51.15
            },
            {
                "no": 12,
                "name": "Euro",
                "currency_code": 978,
                "sign": "EUR",
                "sign_direction": "LEFT",
                "currency_symbol": "€",
                "rate": 1.18
            },
            {
                "no": 13,
                "name": "Hong Kong Dollar",
                "currency_code": 344,
                "sign": "HKD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 10.22
            },
            {
                "no": 14,
                "name": "Hungarian Forint",
                "currency_code": 348,
                "sign": "HUF",
                "sign_direction": "LEFT",
                "currency_symbol": "Ft",
                "rate": 461.75
            },
            {
                "no": 15,
                "name": "Indian Rupee",
                "currency_code": 356,
                "sign": "INR",
                "sign_direction": "LEFT",
                "currency_symbol": "₹",
                "rate": 110.85
            },
            {
                "no": 16,
                "name": "Indonesian Rupiah",
                "currency_code": 360,
                "sign": "IDR",
                "sign_direction": "LEFT",
                "currency_symbol": "Rp",
                "rate": 20586.75
            },
            {
                "no": 17,
                "name": "Iranian Rial",
                "currency_code": 364,
                "sign": "IRR",
                "sign_direction": "LEFT",
                "currency_symbol": "﷼",
                "rate": 55000.0
            },
            {
                "no": 18,
                "name": "Iraqi Dinar",
                "currency_code": 368,
                "sign": "IQD",
                "sign_direction": "LEFT",
                "currency_symbol": "د.ع",
                "rate": 1713.75
            },
            {
                "no": 19,
                "name": "Israeli Shekel",
                "currency_code": 376,
                "sign": "ILS",
                "sign_direction": "LEFT",
                "currency_symbol": "₪",
                "rate": 4.72
            },
            {
                "no": 20,
                "name": "Japanese Yen",
                "currency_code": 392,
                "sign": "JPY",
                "sign_direction": "LEFT",
                "currency_symbol": "¥",
                "rate": 193.45
            },
            {
                "no": 21,
                "name": "Kuwaiti Dinar",
                "currency_code": 414,
                "sign": "KWD",
                "sign_direction": "LEFT",
                "currency_symbol": "د.ك",
                "rate": 0.40
            },
            {
                "no": 22,
                "name": "Malaysian Ringgit",
                "currency_code": 458,
                "sign": "MYR",
                "sign_direction": "LEFT",
                "currency_symbol": "RM",
                "rate": 5.89
            },
            {
                "no": 23,
                "name": "Mexican Peso",
                "currency_code": 484,
                "sign": "MXN",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 26.42
            },
            {
                "no": 24,
                "name": "New Zealand Dollar",
                "currency_code": 554,
                "sign": "NZD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 2.21
            },
            {
                "no": 25,
                "name": "Norwegian Krone",
                "currency_code": 578,
                "sign": "NOK",
                "sign_direction": "LEFT",
                "currency_symbol": "kr",
                "rate": 14.86
            },
            {
                "no": 26,
                "name": "Philippine Peso",
                "currency_code": 608,
                "sign": "PHP",
                "sign_direction": "LEFT",
                "currency_symbol": "₱",
                "rate": 73.62
            },
            {
                "no": 27,
                "name": "Polish Zloty",
                "currency_code": 985,
                "sign": "PLN",
                "sign_direction": "LEFT",
                "currency_symbol": "zł",
                "rate": 5.15
            },
            {
                "no": 28,
                "name": "Qatari Riyal",
                "currency_code": 634,
                "sign": "QAR",
                "sign_direction": "LEFT",
                "currency_symbol": "ر.ق",
                "rate": 4.77
            },
            {
                "no": 29,
                "name": "Romanian Leu",
                "currency_code": 946,
                "sign": "RON",
                "sign_direction": "LEFT",
                "currency_symbol": "lei",
                "rate": 5.85
            },
            {
                "no": 30,
                "name": "Russian Ruble",
                "currency_code": 643,
                "sign": "RUB",
                "sign_direction": "LEFT",
                "currency_symbol": "₽",
                "rate": 101.25
            },
            {
                "no": 31,
                "name": "Saudi Arabian Riyal",
                "currency_code": 682,
                "sign": "SAR",
                "sign_direction": "LEFT",
                "currency_symbol": "ر.س",
                "rate": 4.91
            },
            {
                "no": 32,
                "name": "Singapore Dollar",
                "currency_code": 702,
                "sign": "SGD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1.76
            },
            {
                "no": 33,
                "name": "South African Rand",
                "currency_code": 710,
                "sign": "ZAR",
                "sign_direction": "LEFT",
                "currency_symbol": "R",
                "rate": 24.17
            },
            {
                "no": 34,
                "name": "South Korean Won",
                "currency_code": 410,
                "sign": "KRW",
                "sign_direction": "LEFT",
                "currency_symbol": "₩",
                "rate": 1789.65
            },
            {
                "no": 35,
                "name": "Swedish Krona",
                "currency_code": 752,
                "sign": "SEK",
                "sign_direction": "LEFT",
                "currency_symbol": "kr",
                "rate": 14.72
            },
            {
                "no": 36,
                "name": "Swiss Franc",
                "currency_code": 756,
                "sign": "CHF",
                "sign_direction": "LEFT",
                "currency_symbol": "Fr",
                "rate": 1.17
            },
            {
                "no": 37,
                "name": "Thai Baht",
                "currency_code": 764,
                "sign": "THB",
                "sign_direction": "LEFT",
                "currency_symbol": "฿",
                "rate": 47.85
            },
            {
                "no": 38,
                "name": "Turkish Lira",
                "currency_code": 949,
                "sign": "TRY",
                "sign_direction": "LEFT",
                "currency_symbol": "₺",
                "rate": 35.21
            },
            {
                "no": 39,
                "name": "UAE Dirham",
                "currency_code": 784,
                "sign": "AED",
                "sign_direction": "LEFT",
                "currency_symbol": "د.إ",
                "rate": 4.81
            },
            {
                "no": 40,
                "name": "US Dollar",
                "currency_code": 840,
                "sign": "USD",
                "sign_direction": "LEFT",
                "currency_symbol": "$",
                "rate": 1.31
            }
        ]
        
        for currency_data in currencies:
            currency = Currency(
                no=currency_data["no"],
                name=currency_data["name"],
                currency_code=currency_data["currency_code"],
                sign=currency_data["sign"],
                sign_direction=currency_data["sign_direction"],
                currency_symbol=currency_data["currency_symbol"],
                rate=currency_data["rate"]
            )
            session.add(currency)
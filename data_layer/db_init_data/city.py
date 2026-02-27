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

from data_layer.model import City, Country



from core.logger import get_logger

logger = get_logger(__name__)

def _insert_cities(session):
    """Insert UK cities if not exists"""
    city_exists = session.query(City).first()
    if not city_exists:
        # First, get the UK country ID
        uk_country = session.query(Country).filter_by(iso_alpha2="GB").first()
        if not uk_country:
            logger.error("⚠ UK country not found, skipping city insertion")
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

        logger.info("✓ UK cities added (74 cities)")

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

from data_layer.model import District, City


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

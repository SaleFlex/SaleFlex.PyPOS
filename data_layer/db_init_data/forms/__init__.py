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

# Form and form-control definitions, split by topic/module.
# Each sub-module exposes:
#   get_form_data(cashier_id)           -> list[dict]          (form rows)
#   get_form_controls(form, cashier_id) -> list[FormControl]   (simple forms)
#   insert_*_controls(session, form, cashier_id)               (tab/panel-based forms)

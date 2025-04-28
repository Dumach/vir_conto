# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PrimaryKey(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		conto_name: DF.Data
		conto_primary_key: DF.Data
		enabled: DF.Check
		frappe_name: DF.Data
		import_order: DF.Int
		type: DF.Data | None
		updateable: DF.Check
	# end: auto-generated types

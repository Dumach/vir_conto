# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class primarykey(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cconto_name: DF.Data
		cconto_pkey: DF.Data
		frappe_name: DF.Data
		import_order: DF.Int
		is_enabled: DF.Check
		is_updateable: DF.Check
		type: DF.Data | None
	# end: auto-generated types

	def validate(self):
		pass

# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class vir_csop(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bert: DF.Int
		csop: DF.Data
		datum: DF.Data
		ho: DF.Data
		nert: DF.Int
		rkod: DF.Link
		tipus: DF.Link
	# end: auto-generated types

	pass

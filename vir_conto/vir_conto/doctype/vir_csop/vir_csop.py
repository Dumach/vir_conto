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

		bert: DF.Currency
		csop: DF.Link | None
		datum: DF.Date
		ev: DF.Int
		ho: DF.Int
		nert: DF.Currency
		rkod: DF.Link
		tipus: DF.Data
	# end: auto-generated types

	def before_save(self):
		self.ev = self.datum.year

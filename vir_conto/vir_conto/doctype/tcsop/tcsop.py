# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class tcsop(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		focsop: DF.Link
		kod: DF.Data
		nev: DF.Data
		rend: DF.Int
		tarhely: DF.Data
	# end: auto-generated types

	from typing import TYPE_CHECKING
	pass

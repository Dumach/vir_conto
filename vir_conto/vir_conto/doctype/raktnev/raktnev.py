# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class raktnev(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		boltkat: DF.Data
		cim_kod: DF.Data
		f_kod: DF.Link
		gyszam: DF.Data
		keszletkez: DF.Data
		megye: DF.Data
		nagyker: DF.Data
		negativk: DF.Data
		rcim: DF.Data
		rirsz: DF.Data
		rkod: DF.Data
		rnev: DF.Data
		rtel: DF.Data
		rvaros: DF.Data
		sorrend: DF.Int
	# end: auto-generated types

	pass

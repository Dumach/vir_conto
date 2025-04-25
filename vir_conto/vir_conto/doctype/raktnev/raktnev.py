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

		boltkat: DF.Data | None
		cim_kod: DF.Data | None
		f_kod: DF.Link | None
		gyszam: DF.Data | None
		keszletkez: DF.Data | None
		megye: DF.Data | None
		nagyker: DF.Data | None
		negativk: DF.Data | None
		rcim: DF.Data | None
		rirsz: DF.Data | None
		rkod: DF.Data
		rnev: DF.Data
		rtel: DF.Data | None
		rvaros: DF.Data | None
		sorrend: DF.Int
	# end: auto-generated types

	pass

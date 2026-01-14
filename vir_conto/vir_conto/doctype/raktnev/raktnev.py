# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
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

	@frappe.whitelist()
	def update_raktnev(self):
		"""
		Updates raktnev in vir_bolt based on the current rnev in raktnev table

		update vir_bolt vb set rnev=(select rnev from raktnev rn where rn.rkod=vb.rkod)
		--where rkod='200'
		"""

		vir_bolt = frappe.qb.DocType("vir_bolt")
		frappe.qb.update(vir_bolt).set(vir_bolt.rnev, self.rnev).where(vir_bolt.rkod == self.rkod).run()
		frappe.db.commit()
		return _("Finished")

# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class vir_bolt(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bbesz_kp: DF.Int
		bbesz_nkp: DF.Int
		bert_eng: DF.Int
		bert_ossz: DF.Int
		bsaj_felh: DF.Int
		bselejt: DF.Int
		bszallrend: DF.Int
		datum: DF.Date
		haszon: DF.Int
		hkulcs: DF.Float
		ho: DF.Data | None
		keszlet: DF.Int
		kosara: DF.Int
		nbesz_kp: DF.Int
		nbesz_nkp: DF.Int
		neg_keszlm: DF.Int
		nert_ossz: DF.Int
		nszallrend: DF.Int
		rkod: DF.Link
		rnev: DF.Data | None
		vevok: DF.Int
	# end: auto-generated types

	pass

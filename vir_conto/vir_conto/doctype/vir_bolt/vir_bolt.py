# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cast


class vir_bolt(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bbesz_kp: DF.Currency
		bbesz_nkp: DF.Currency
		bert_eng: DF.Currency
		bert_ossz: DF.Currency
		bsaj_felh: DF.Currency
		bselejt: DF.Currency
		bszallrend: DF.Currency
		datum: DF.Date
		ev: DF.Int
		haszon: DF.Float
		hkulcs: DF.Float
		ho: DF.Int
		ho_nap: DF.Int
		keszlet: DF.Currency
		kosara: DF.Currency
		nbesz_kp: DF.Currency
		nbesz_nkp: DF.Currency
		neg_keszlm: DF.Currency
		nert_ossz: DF.Currency
		nszallrend: DF.Currency
		rkod: DF.Link
		rnev: DF.Data
		vevok: DF.Int
	# end: auto-generated types

	def before_save(self):
		self.set_dates()

	def set_dates(self):
		date = cast("Date", self.datum)
		self.ev = date.year
		self.ho = date.month
		self.ho_nap = self.datum[5:7] + self.datum[8:10]

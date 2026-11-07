# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

from datetime import date

import frappe
from frappe.model.document import Document
from frappe.utils import cast, cint


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
		ho_nap: DF.Int
		nert: DF.Currency
		rkod: DF.Link
		tipus: DF.Data
	# end: auto-generated types

	def autoname(self) -> None:
		datum = str(self.datum).replace('-', '.')
		self.name = f"{self.tipus}/{self.csop}/{self.rkod}/{datum}"

	def before_save(self) -> None:
		self.set_dates()

	def set_dates(self) -> None:
		create_date: date = cast("Date", self.datum)
		self.ev = create_date.year
		self.ho = create_date.month
		self.ho_nap = self.datum[5:7] + self.datum[8:10]

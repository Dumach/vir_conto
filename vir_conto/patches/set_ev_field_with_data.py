import frappe
from pypika import CustomFunction


def execute():
	"""Set `ev` field with data from `datum` in vir_bolt, vir_csop

	UPDATE `tabvir_bolt`
	SET ev = YEAR(datum);
	"""

	toYear = CustomFunction("YEAR", ["date"])

	# vir_bolt
	table = frappe.qb.DocType("vir_bolt")
	query = frappe.qb.update(table).set(table.ev, toYear(table.datum))
	query.run()

	# vir_csop
	table = frappe.qb.DocType("vir_csop")
	query = frappe.qb.update(table).set(table.ev, toYear(table.datum))
	query.run()

import frappe
from frappe.utils import cast


def execute():
	"""Fill ev column with year data in vir_bolt, vir_csop"""

	docs = frappe.db.get_list("vir_bolt", filters={"ev": None}, pluck="name")
	for doc_name in docs:
		doc = frappe.get_doc("vir_bolt", doc_name)
		doc.db_set("ev", cast("Date", doc.datum).year)

	docs = frappe.db.get_list("vir_csop", filters={"ev": None}, pluck="name")
	for doc_name in docs:
		doc = frappe.get_doc("vir_csop", doc_name)
		doc.db_set("ev", cast("Date", doc.datum).year)

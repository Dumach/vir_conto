import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"Insights Workbook": [
			{
				"fieldname": "is_default",
				"fieldtype": "Check",
				"label": "Is Default",
				"default": 0,
				"read_only": 1,
				"insert_after": "title",
				"description": "Indicates if this workbook is a default vir_conto workbook",
				"no_copy": 1,
				"print_hide": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"search_index": 1,
			},
			{
				"fieldname": "vir_id",
				"fieldtype": "Data",
				"label": "Vir ID",
				"unique": 1,
				"read_only": 1,
				"insert_after": "is_default",
				"description": "Unique identifier for vir_conto workbook synchronization",
				"no_copy": 1,
				"print_hide": 1,
				"search_index": 1,
				"depends_on": "is_default",
			},
		]
	}

	create_custom_fields(custom_fields)

	# Generate vir_id for workbooks
	frappe.reload_doctype("Insights Workbook")
	workbooks = frappe.db.get_list("Insights Workbook")
	for wb in workbooks:
		workbook = frappe.get_doc("Insights Workbook", wb)
		workbook.generate_vir_id()
	frappe.db.commit()

	print("Successfully added is_default and vir_id custom fields to Insights Workbook")

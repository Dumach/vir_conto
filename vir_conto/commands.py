import click
import frappe
from frappe.commands import pass_context
from frappe.exceptions import SiteNotSpecifiedError
from frappe.utils.fixtures import export_json


@click.command("export-default-charts")
@pass_context
def export_insights(context):
	"""Command wrapper for export_default_charts().

	Args:
	        context (_type_): Frappe site context.

	Raises:
	        SiteNotSpecifiedError: If site is not provided or can not connect to.
	"""

	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			export_default_charts()
		finally:
			frappe.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


def export_default_charts():
	"""Method for exporting Insights Queries, Charts, Dashboards."""
	app = "vir_conto"

	# Find workbooks by title pattern (starting with "_") or already marked as default
	default_workbooks = frappe.get_all(
		"Insights Workbook",
		fields=[
			"name",
			"title",
		],
		filters={"is_default": True},
	)

	if len(default_workbooks) < 1:
		print("No default workbook found")
		return

	# Generate vir_id and set is_default for workbooks that don't have them
	for wb in default_workbooks:
		workbook = frappe.get_doc("Insights Workbook", wb)
		workbook.generate_vir_id()

	default_workbook_names = [wb["name"] for wb in default_workbooks]

	fixtures = [
		{"dt": "Insights Workbook", "filters": [["name", "in", default_workbook_names]]},
		{"dt": "Insights Query v3", "filters": [["workbook", "in", default_workbook_names]]},
		{"dt": "Insights Chart v3", "filters": [["workbook", "in", default_workbook_names]]},
		{"dt": "Insights Dashboard v3", "filters": [["workbook", "in", default_workbook_names]]},
	]

	for fixture in fixtures:
		export_json(
			fixture.get("dt"),
			frappe.get_app_path(app, "charts", frappe.scrub(str(fixture.get("dt"))) + ".json"),
			filters=fixture.get("filters"),
			or_filters=fixture.get("or_filters"),
			order_by="idx asc, creation asc",
		)

	print(f"{len(default_workbooks)} default workbook(s) found")


commands = [export_insights]

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

	default_workbooks = [
		wb["name"]
		for wb in frappe.get_all("Insights Workbook", fields=["name", "title"])
		if wb["title"].startswith("_")
	]

	if len(default_workbooks) < 1:
		print("No default workbook found")
		return

	fixtures = [
		{"dt": "Insights Workbook", "filters": [["name", "in", default_workbooks]]},
		{"dt": "Insights Query v3", "filters": [["workbook", "in", default_workbooks]]},
		{"dt": "Insights Chart v3", "filters": [["workbook", "in", default_workbooks]]},
		{"dt": "Insights Dashboard v3", "filters": [["workbook", "in", default_workbooks]]},
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

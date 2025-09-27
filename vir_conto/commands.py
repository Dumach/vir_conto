import os

import click
import frappe
from frappe.commands import pass_context
from frappe.core.doctype.data_import.data_import import export_json
from frappe.exceptions import SiteNotSpecifiedError

from vir_conto.overrides.insights_workbook import CustomInsightsWorkbook


@click.command("export-insights")
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

			save_path = frappe.get_app_path("vir_conto", "charts")

			count = export_default_charts(save_path)
			if count > 0:
				print(f"{count} default workbook(s) found")
			else:
				print("No default workbook found")

		finally:
			frappe.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


def export_default_charts(base_path: str) -> int:
	"""
	Method for exporting Insights Workbooks, Queries, Charts, Dashboards.

	Args:
	        base_path: Base path of which the files will be exported.
	"""

	default_workbooks = frappe.get_all("Insights Workbook", filters={"is_default": True})

	if len(default_workbooks) < 1:
		return 0

	# Generate vir_id and set is_default for workbooks that don't have them
	for wb in default_workbooks:
		workbook: CustomInsightsWorkbook = frappe.get_doc("Insights Workbook", wb)
		workbook.generate_vir_id()

	default_workbooks = [wb["name"] for wb in default_workbooks]

	fixtures = [
		{"dt": "Insights Workbook", "filters": [["name", "in", default_workbooks]]},
		{"dt": "Insights Query v3", "filters": [["workbook", "in", default_workbooks]]},
		{"dt": "Insights Chart v3", "filters": [["workbook", "in", default_workbooks]]},
		{"dt": "Insights Dashboard v3", "filters": [["workbook", "in", default_workbooks]]},
	]

	for fixture in fixtures:
		path = os.path.join(base_path, frappe.scrub(fixture["dt"] + ".json"))
		export_json(
			doctype=fixture.get("dt"),
			path=path,
			filters=fixture.get("filters"),
			or_filters=fixture.get("or_filters"),
			order_by="idx asc, creation asc",
		)
	return len(default_workbooks)


commands = [export_insights]

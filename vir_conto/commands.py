import click
import frappe
from frappe.commands import pass_context
from frappe.exceptions import SiteNotSpecifiedError
from frappe.utils.fixtures import export_json


@click.command("export-insights")
@pass_context
def export_insights(context):
	# Queries, Charts, Dashboards
	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			export()
		finally:
			frappe.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


def export():
	app = "vir_conto"
	fixtures = [
		{"dt": "Insights Workbook", "filters": [["title", "like", "_%"]]},
		{
			"dt": "Insights Query v3",
			"filters": [
				[
					"workbook",
					"in",
					frappe.db.get_all("Insights Workbook", filters=[["title", "like", "_%"]], pluck="name"),
				]
			],
		},
		{"dt": "Insights Chart v3", "filters": [["title", "like", "_%"]]},
		{"dt": "Insights Dashboard v3", "filters": [["title", "like", "_%"]]},
	]

	for fixture in fixtures:
		export_json(
			fixture.get("dt"),
			frappe.get_app_path(app, "charts", frappe.scrub(fixture.get("dt")) + ".json"),
			filters=fixture.get("filters"),
			or_filters=fixture.get("or_filters"),
			order_by="idx asc, creation asc",
		)


commands = [export_insights]

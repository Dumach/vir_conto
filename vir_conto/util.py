import frappe
import frappe.hooks
from frappe.modules.import_file import read_doc_from_file
from insights.insights.doctype.insights_chart_v3.insights_chart_v3 import InsightsChartv3
from insights.insights.doctype.insights_dashboard_v3.insights_dashboard_v3 import InsightsDashboardv3
from insights.insights.doctype.insights_query_v3.insights_query_v3 import InsightsQueryv3
from insights.insights.doctype.insights_workbook.insights_workbook import InsightsWorkbook


def get_frappe_version() -> str:
	"""
	Returns Frappe version from environment variable.

	:return	str: Frappe version number in string.
	"""
	return frappe.hooks.app_version


def sync_default_charts():
	"""
	Synchronize default Insights charts, queries, and dashboards with the database.

	This function ensures that the default Insights workbooks, queries, charts, and dashboards
	are up-to-date in the database by performing the following steps:

	1. Import old workbooks from the JSON file 'insights_workbook.json' located in the 'charts' directory.
	2. Insert any missing workbooks into the database based on their title.
	3. Retrieve all workbooks from the database whose title starts with '_'.
	4. Build a lookup table to map old workbook names to their new IDs and titles.
	5. For each of the following doctypes: 'insights_query_v3', 'insights_chart_v3', 'insights_dashboard_v3':
	   - Delete existing records in the database that reference the new workbook IDs (to remove outdated defaults).
	   - Import documents from their respective JSON files.
	   - Update the workbook reference in each imported document to the new workbook ID.
	   - Insert the document into the database, overwriting if it already exists.
	6. Commit all changes to the database.

	Notes:
	- All required JSON files must be present in the 'charts' directory of the 'vir_conto' app.
	- Workbook titles are assumed to be unique and are used for mapping.
	- If any required JSON file is missing, the function prints a message and exits early.
	"""
	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	path = frappe.get_app_path("vir_conto", "charts", "insights_workbook.json")

	# 1. (OLD) Import old title and name of workbook from JSON
	try:
		docs = read_doc_from_file(path)
	except OSError:
		logger.exception(f"{path} missing")
		return

	if docs:
		if not isinstance(docs, list):
			docs = [docs]
		old_workbooks: list[InsightsWorkbook] = [frappe.get_doc(doc) for doc in docs]

	# 2. Check if a default workbook exists
	for old_workbook in old_workbooks:
		if not frappe.db.exists("Insights Workbook", {"title": old_workbook.title}):
			# If not creates a new
			old_workbook.insert()

	# 3. (NEW) Get all workbooks title and name
	new_workbooks = [
		wb for wb in frappe.get_all("Insights Workbook", fields=["*"]) if wb["title"].startswith("_")
	]

	# 4. Create lookup table for migrating queries, charts, dashboards
	workbook_lookup = {}
	for new_workbook in new_workbooks:
		# Configure Organization Access
		from insights.utils import DocShare

		public_docshare = DocShare.get_or_create_doc(
			share_doctype="Insights Workbook",
			share_name=new_workbook.name,
			everyone=1,
		)
		public_docshare.read = 1
		public_docshare.write = 0
		public_docshare.notify_by_email = 0
		public_docshare.save(ignore_permissions=True)

		# Create lookup Table
		for old_workbook in old_workbooks:
			if old_workbook.title == new_workbook.title:
				workbook_lookup[old_workbook.name] = {
					"new_id": new_workbook.name,
					"title": old_workbook.title,
				}
				break

	# 5. Clearing tables, in case if a default chart no longer needed
	# This ensures that removed default charts won't remain in client database
	doctypes = ["Insights Query v3", "Insights Chart v3", "Insights Dashboard v3"]
	for doctype in doctypes:
		for _, value in workbook_lookup.items():
			frappe.db.delete(doctype, filters={"workbook": value["new_id"]})

	# 6. Import the rest (queries, charts, dashboards)
	doctypes = ["insights_query_v3", "insights_chart_v3", "insights_dashboard_v3"]
	for doctype in doctypes:
		path = frappe.get_app_path("vir_conto", "charts", doctype + ".json")
		try:
			docs = read_doc_from_file(path)
		except OSError:
			logger.exception(f"{path} missing")
			return

		if docs:
			if not isinstance(docs, list):
				docs = [docs]
			for doc in docs:
				old_doc: InsightsQueryv3 | InsightsChartv3 | InsightsDashboardv3 = frappe.get_doc(doc)

				# 7. update workbook name accordingly
				workbook_id = old_doc.workbook

				# must be parsed to int otherwise fails to get key
				lookup = workbook_lookup.get(int(workbook_id))
				if not lookup:
					logger.warning(
						f"No workbook mapping found for title: {workbook_id}, skipping old_doc: {old_doc.name}"
					)
					continue

				new_id = lookup["new_id"]
				old_doc.workbook = new_id

				old_doc.insert(ignore_links=True, set_name=old_doc.name)

			frappe.db.commit()  # nosemgrep

import frappe
from frappe.modules.import_file import read_doc_from_file
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
		import_workbooks: list[InsightsWorkbook] = [frappe.get_doc(doc) for doc in docs]

	# 2. Check if a default workbook exists
	for import_workbook in import_workbooks:
		if not frappe.db.exists("Insights Workbook", {"title": import_workbook.title}):
			# If not creates a new
			import_workbook.insert()

	# 3. (NEW) Get all workbooks title and name
	new_workbooks = [
		wb for wb in frappe.get_all("Insights Workbook", fields=["*"]) if wb["title"].startswith("_")
	]

	# 4. Create lookup table for migrating queries, charts, dashboards
	workbook_dict = {}
	for new_workbook in new_workbooks:
		new_title = new_workbook.title
		new_id = new_workbook.name
		match_name = next(
			import_workbook.name for import_workbook in import_workbooks if import_workbook.title == new_title
		)

		workbook_dict[match_name] = {"new_id": new_id, "new_title": new_title}

	# 5. Clearing tables, in case if a default chart no longer needed
	# This ensures that removed default charts won't remain in client database
	doctypes = ["Insights Query v3", "Insights Chart v3", "Insights Dashboard v3"]
	for doctype in doctypes:
		for _, value in workbook_dict.items():
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
				import_doc = frappe.get_doc(doc)

				# 7. update workbook name accordingly
				old_id = import_doc.workbook

				new_id = workbook_dict.get(int(old_id))["new_id"]
				import_doc.workbook = new_id

				import_doc.insert(ignore_links=True, set_name=import_doc.name)

			frappe.db.commit()  # nosemgrep

import os
from typing import Any, Optional

import frappe
import frappe.hooks
from frappe.modules.import_file import read_doc_from_file
from insights.insights.doctype.insights_chart_v3.insights_chart_v3 import InsightsChartv3
from insights.insights.doctype.insights_dashboard_v3.insights_dashboard_v3 import InsightsDashboardv3
from insights.insights.doctype.insights_query_v3.insights_query_v3 import InsightsQueryv3
from insights.insights.doctype.insights_workbook.insights_workbook import InsightsWorkbook

PRINT = True


def get_frappe_version() -> str:
	"""
	Returns Frappe version from environment variable.

	:return	str: Frappe version number in string.
	"""
	return frappe.hooks.app_version


def load_documents_from_json(file_name: str, doctype_name: str, logger) -> list[Any] | None:
	"""
	Load and validate documents from a JSON file in the charts directory.

	Args:
	        file_name: Name of the JSON file (with or without .json extension)
	        doctype_name: Name of the doctype for logging purposes
	        logger: Logger instance for error reporting

	Returns:
	        List of Frappe documents or None if loading failed
	"""
	try:
		path = frappe.get_app_path("vir_conto", "charts", file_name)

		if not os.path.exists(path):
			msg = f"{doctype_name} file not found: {path}"
			logger.error(msg)
			if PRINT:
				print(msg)
			return None

		docs = read_doc_from_file(path)

		if not docs:
			msg = f"No {doctype_name} found in file"
			logger.warning(msg)
			if PRINT:
				print(msg)
			return None

		if not isinstance(docs, list):
			docs = [docs]

		# Convert to Frappe documents
		frappe_docs = [frappe.get_doc(doc) for doc in docs]

		return frappe_docs

	except OSError as e:
		msg = f"File system error loading {doctype_name}: {str(e)}"
		logger.error(msg)
		if PRINT:
			print(msg)
		return None
	except Exception as e:
		msg = f"Unexpected error loading {doctype_name}: {str(e)}"
		logger.exception(msg)
		if PRINT:
			print(msg)
		return None


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
	logger.setLevel("INFO")

	try:
		# frappe.db.begin()

		# Step 1: Load workbooks from `charts/insights_workbook.json`
		import_workbooks = load_documents_from_json("insights_workbook.json", "workbooks", logger)
		if not import_workbooks:
			msg = "No workbooks found to import, aborting synchronization"
			logger.error(msg)
			if PRINT:
				print(msg)
			return False

		# Step 2: Create new workbooks if not exist already
		for import_workbook in import_workbooks:
			if not frappe.db.exists("Insights Workbook", {"vir_id": import_workbook.vir_id}):
				# Ensure the workbook is marked as default
				import_workbook.is_default = 1
				# If not creates a new
				import_workbook.insert()

		# Step 3: Get existing workbooks and create lookup table
		workbook_lookup = _create_workbook_lookup(import_workbooks, logger)
		if not workbook_lookup:
			msg = "Failed to create workbook lookup table, aborting synchronization"
			logger.error(msg)
			if PRINT:
				print(msg)
			return False

		# Step 4: Clean existing default records,
		#  in case if a default chart no longer needed
		doctypes = ["Insights Query v3", "Insights Chart v3", "Insights Dashboard v3"]
		_clean_existing_records(workbook_lookup, doctypes, logger)

		# Step 5: Import queries, charts, dashboards for each workbook
		_import_charts(workbook_lookup, doctypes, logger)

	except Exception as e:
		msg = f"Failed to sync default charts: {str(e)}"
		logger.exception(msg)
		if PRINT:
			print(msg)
		# frappe.db.rollback()
		return

	# Commit all changes
	frappe.db.commit()


def _create_workbook_lookup(import_workbooks, logger):
	try:
		# Step 3: Get the workbook ID's from the new system
		new_workbooks = frappe.get_all(
			"Insights Workbook", fields=["name", "title", "vir_id"], filters={"is_default": 1}
		)

		# 4. Create lookup table for migrating queries, charts, dashboards
		workbook_lookup = {}
		for new_workbook in new_workbooks:
			# Configure organization access
			configure_workbook_access(new_workbook, logger)

			# Create lookup mapping using vir_id
			for import_workbook in import_workbooks:
				if import_workbook.vir_id == new_workbook.vir_id:
					workbook_lookup[import_workbook.name] = {
						"new_id": new_workbook.name,
						"vir_id": import_workbook.vir_id,
					}
					break

		return workbook_lookup

	except Exception as e:
		msg = f"Failed to create workbook lookup table: {str(e)}"
		logger.exception(msg)
		if PRINT:
			print(msg)
		# return None
		frappe.throw("Failed to create workbook lookup table")


def configure_workbook_access(workbook, logger):
	"""Configure public access for a workbook."""
	try:
		from insights.utils import DocShare

		public_docshare = DocShare.get_or_create_doc(
			share_doctype="Insights Workbook",
			share_name=workbook.name,
			everyone=1,
		)
		public_docshare.read = 1
		public_docshare.write = 0
		public_docshare.notify_by_email = 0
		public_docshare.save(ignore_permissions=True)

	except Exception as e:
		logger.error(
			f"Failed to configure access for workbook '{workbook.get('title', 'Unknown')}': {str(e)}"
		)
		# Don't raise - this is not critical for the main functionality


def _clean_existing_records(workbook_lookup, doctypes, logger):
	# This ensures that removed default charts won't remain in client database
	for dt in doctypes:
		try:
			for _, value in workbook_lookup.items():
				frappe.db.delete(dt, filters={"workbook": value["new_id"]})

		except Exception as e:
			msg = f"Failed to clean existing records for {dt}: {str(e)}"
			logger.error(msg)
			if PRINT:
				print(msg)


def _import_charts(workbook_lookup, doctypes, logger):
	for dt in doctypes:
		try:
			# Load documents using the reusable function
			docs = load_documents_from_json(frappe.scrub(dt) + ".json", dt, logger)
			if not docs:
				msg = f"No {dt} found, skipping"
				logger.warning(msg)
				if PRINT:
					print(msg)
				continue

			for doc in docs:
				old_doc: InsightsQueryv3 | InsightsChartv3 | InsightsDashboardv3 = doc

				# Update workbook name accordingly
				workbook_id = old_doc.workbook

				# Must be parsed to int otherwise fails to get key
				try:
					lookup = workbook_lookup.get(int(workbook_id))
					if not lookup:
						msg = f"No workbook mapping found for workbook_id: {workbook_id}, skipping old_doc: {old_doc.name}"
						logger.warning(msg)
						if PRINT:
							print(msg)
						continue

					old_doc.workbook = lookup["new_id"]
					old_doc.insert(ignore_links=True, set_name=old_doc.name)
				except Exception as e:
					msg = f"Failed to process {dt} document {old_doc.name}: {str(e)}"
					logger.error(msg)
					if PRINT:
						print(msg)
					continue

		except Exception as e:
			msg = f"Failed to import {dt}: {str(e)}"
			logger.exception(msg)
			print(msg)
			continue

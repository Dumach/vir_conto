import os
from logging import Logger
from typing import TypedDict

import frappe
from frappe.model.document import Document
from frappe.modules.import_file import read_doc_from_file

from vir_conto.overrides.insights_workbook import CustomInsightsWorkbook


class WorkbookInfo(TypedDict):
	new_id: str
	vir_id: str


def load_documents_from_json(path: str, dt: str, logger: Logger) -> list[Document] | None:
	"""
	Load and validate documents from a JSON file in the charts directory.

	Args:
	        path: Absolute path of the JSON file (with or without .json extension)
	        dt: Name of the doctype for logging purpose
	        logger: Logger instance for error reporting

	Returns:
	        List of Frappe documents or None if loading failed
	"""
	try:
		if not os.path.exists(path):
			logger.error(f"{dt} file not found: {path}")
			return None

		docs = read_doc_from_file(path)

		if not docs:
			logger.warning(f"No {dt} found in file: {path}")
			return None

		if not isinstance(docs, list):
			docs = [docs]

		# Convert to Frappe documents
		frappe_docs = [frappe.get_doc(doc) for doc in docs]
		return frappe_docs

	except Exception as e:
		logger.exception(f"Unexpected error loading {dt} from {path}: {e}")
		return None


def sync_default_charts(base_path="") -> None:
	"""Synchronizes default Insights items with the database.

	This function uses JSON files from the 'charts' directory to perform the following:

	- **Workbooks**:
	  - Imports workbooks from `insights_workbook.json`.
	  - Removes default workbooks and their contents if they are no longer in the import file.
	  - Creates new workbooks as needed.
	- **Charts, Queries, and Dashboards**:
	  - Clears existing default records to prevent outdated data.
	  - Imports and links `Insights Query v3`, `Insights Chart v3`, and `Insights Dashboard v3` documents to their respective workbooks.
	"""

	logger: Logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	logger.setLevel("INFO")

	try:
		if base_path == "":
			base_path = os.path.join(frappe.get_app_path("vir_conto"), "charts")

		# Step 1: Load workbooks from `charts/insights_workbook.json`
		path = os.path.join(base_path, "insights_workbook.json")
		import_workbooks: list[CustomInsightsWorkbook] = load_documents_from_json(path, "Insights Workbook", logger)
		if not import_workbooks:
			logger.error("No workbooks found to import, aborting synchronization.")
			return

		doctypes_to_clean = ["Insights Query v3", "Insights Chart v3", "Insights Dashboard v3"]

		# Step 2: Remove unwanted workbooks
		_remove_old_workbooks(import_workbooks, logger)

		# Step 3: Create new workbooks if not exist already
		_create_new_workbooks(import_workbooks, logger)

		# Step 4: Get existing workbooks and create lookup table
		workbook_lookup = _create_workbook_lookup(import_workbooks, logger)
		if not workbook_lookup:
			logger.error("Failed to create workbook lookup table, aborting synchronization.")
			return

		# Step 5: Remove all queries, charts, dashboards from the workbooks that we keep
		# in order to sync the content of the default workbooks
		default_wb = [wb["new_id"] for wb in workbook_lookup.values()]
		_clean_existing_records(default_wb, logger)

		# Step 6: Import queries, charts, dashboards for each workbook
		_import_charts(workbook_lookup, base_path, doctypes_to_clean, logger)

	except Exception as e:
		logger.exception(f"Failed to sync default charts: {e}")
		return

	frappe.db.commit()


def _remove_old_workbooks(import_workbooks: list[CustomInsightsWorkbook], logger: Logger) -> None:
	"""Remove default workbooks that are no longer in the import file."""
	old_workbooks: list[CustomInsightsWorkbook] = frappe.db.get_all(
		"Insights Workbook", fields=["name", "vir_id"], filters={"is_default": True}
	)
	import_vir_ids = {wb.vir_id for wb in import_workbooks}

	for owb in old_workbooks:
		if owb.vir_id not in import_vir_ids:
			try:
				# _clean_existing_records([str(owb.name)], logger)
				doc = frappe.get_doc("Insights Workbook", str(owb.name))
				doc.delete()
				logger.info(f"Removed old workbook: {owb.name}")
			except Exception as e:
				logger.error(f"Failed to remove old workbook {owb.name}: {e}")


def _create_new_workbooks(import_workbooks: list[CustomInsightsWorkbook], logger: Logger) -> None:
	"""Create new workbooks from the import file if they don't exist."""
	for import_workbook in import_workbooks:
		if not frappe.db.exists("Insights Workbook", {"vir_id": import_workbook.vir_id}):
			try:
				wb: CustomInsightsWorkbook = frappe.get_doc(import_workbook.as_dict())
				wb.set("is_default", 1)
				wb.insert()
				logger.info(f"Created new workbook: {wb.title}")
			except Exception as e:
				logger.error(f"Failed to create new workbook {import_workbook.title}: {e}")


def _create_workbook_lookup(
	import_workbooks: list[CustomInsightsWorkbook], logger: Logger
) -> dict[int, WorkbookInfo] | None:
	"""Create a lookup table for workbook IDs."""

	try:
		new_workbooks: list[CustomInsightsWorkbook] = frappe.get_all(
			"Insights Workbook", fields=["name", "title", "vir_id"], filters={"is_default": 1}
		)

		import_workbook_map = {wb.vir_id: wb for wb in import_workbooks}
		workbook_lookup: dict[int, WorkbookInfo] = {}

		for new_workbook in new_workbooks:
			_configure_workbook_access(new_workbook, logger)
			import_workbook = import_workbook_map.get(new_workbook.vir_id)
			if import_workbook:
				workbook_lookup[import_workbook.name] = {
					"new_id": new_workbook.name,
					"vir_id": import_workbook.vir_id,
				}
		return workbook_lookup

	except Exception as e:
		logger.exception(f"Failed to create workbook lookup table: {e}")
		return None


def _configure_workbook_access(workbook: CustomInsightsWorkbook, logger: Logger) -> None:
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
		logger.error(f"Failed to configure access for workbook '{workbook.get('title', 'Unknown')}': {e}")


def _clean_existing_records(workbook_names: list[str], logger: Logger) -> None:
	"""This ensures that removed default charts won't remain in client database."""
	try:
		frappe.db.delete("Insights Query v3", filters={"workbook": ["in", workbook_names]})
		frappe.db.delete("Insights Chart v3", filters={"workbook": ["in", workbook_names]})
		frappe.db.delete("Insights Dashboard v3", filters={"workbook": ["in", workbook_names]})
	except Exception as e:
		logger.error(f"Failed to clean existing records\n{e}")


def _import_charts(
	workbook_lookup: dict[int, WorkbookInfo], base_path: str, doctypes: list[str], logger: Logger
) -> None:
	for doctype in doctypes:
		dt = frappe.scrub(doctype)
		path = os.path.join(base_path, dt + ".json")
		docs = load_documents_from_json(path, doctype, logger)

		if not docs:
			logger.warning(f"No {doctype} found, skipping")
			continue

		for doc in docs:
			try:
				old_doc = doc
				workbook_id = old_doc.workbook
				lookup = workbook_lookup.get(int(workbook_id))

				if not lookup:
					logger.warning(f"No workbook mapping found for workbook_id: {workbook_id} in {doctype} {doc.name}")
					continue

				old_doc.workbook = lookup["new_id"]
				old_doc.insert(ignore_links=True, set_name=old_doc.name)
			except Exception as e:
				logger.error(f"Failed to process {doctype} document {doc.name}: {e}")
				continue

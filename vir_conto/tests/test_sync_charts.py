import json
import os
import unittest
from unittest.mock import MagicMock, patch

import frappe

from vir_conto.overrides.insights_workbook import CustomInsightsWorkbook
from vir_conto.util import (
	WorkbookInfo,
	_clean_existing_records,
	_create_new_workbooks,
	_create_workbook_lookup,
	_import_charts,
	_remove_old_workbooks,
	load_documents_from_json,
	sync_default_charts,
)


class TestSyncDefaultCharts(unittest.TestCase):
	"""Test suite for sync_default_charts function and related utilities."""

	@classmethod
	def setUpClass(cls):
		"""Set up test class with required test records."""
		frappe.set_user("Administrator")

	def setUp(self):
		"""Set up test data before each test."""
		# Sample test workbook data
		base_path = os.path.join(frappe.get_app_path("vir_conto"), "tests")

		with open(os.path.join(base_path, "insights_workbook.json")) as file:
			self.sample_workbook_data = json.load(file)  # pyright: ignore[reportUninitializedInstanceVariable]

		with open(os.path.join(base_path, "insights_query_v3.json")) as file:
			self.sample_query_data = json.load(file)  # pyright: ignore[reportUninitializedInstanceVariable]

		with open(os.path.join(base_path, "insights_chart_v3.json")) as file:
			self.sample_chart_data = json.load(file)  # pyright: ignore[reportUninitializedInstanceVariable]

		with open(os.path.join(base_path, "insights_dashboard_v3.json")) as file:
			self.sample_dashboard_data = json.load(file)  # pyright: ignore[reportUninitializedInstanceVariable]

	def tearDown(self):
		"""Clean up after each test."""
		frappe.db.rollback()
		# frappe.db.delete("Insights Workbook")

	def test_sync_default_charts_no_workbooks(self):
		"""Test sync function when no workbooks are found."""
		with (
			patch("vir_conto.util.load_documents_from_json") as mock_load,
			patch("vir_conto.util._remove_old_workbooks") as mock_remove,
			patch("frappe.db.commit") as mock_commit,
		):
			mock_load.return_value = None

			# Execute function
			sync_default_charts()

			# Verify early return and no commit
			mock_load.assert_called_once()
			mock_remove.assert_not_called()
			mock_commit.assert_not_called()

	def test_sync_default_charts_workbook_lookup_failure(self):
		"""Test sync function when workbook lookup creation fails."""
		with (
			patch("vir_conto.util.load_documents_from_json") as mock_load,
			patch("vir_conto.util._create_workbook_lookup") as mock_lookup,
			patch("frappe.db.commit") as mock_commit,
		):
			mock_workbooks = [CustomInsightsWorkbook(wb) for wb in self.sample_workbook_data]
			mock_load.return_value = mock_workbooks
			mock_lookup.return_value = None

			# Execute function
			sync_default_charts()

			# Verify early return after lookup failure
			mock_lookup.assert_called_once()
			mock_commit.assert_not_called()

	def test_sync_default_charts_exception_handling(self):
		"""Test sync function handles exceptions properly."""
		with (
			patch("vir_conto.util.load_documents_from_json") as mock_load,
			patch("frappe.db.commit") as mock_commit,
		):
			mock_load.side_effect = Exception("Test exception")

			# Execute function - should not raise exception
			sync_default_charts()

			# Verify no commit on exception
			mock_commit.assert_not_called()

	def test_load_documents_from_json_success(self):
		"""Test successful loading of documents from file."""
		mock_logger = MagicMock()

		path = os.path.join(frappe.get_app_path("vir_conto"), "tests", "insights_workbook.json")
		results = load_documents_from_json(path=path, dt="Insights Workbook", logger=mock_logger)

		self.assertIsNotNone(results)
		self.assertEqual(len(results), 2)
		mock_logger.error.assert_not_called()

	def test_load_documents_from_json_not_found(self):
		"""Test loading from non-existent file."""
		mock_logger = MagicMock()

		path = os.path.join(frappe.get_app_path("vir_conto"), "tests", "wrong_file.json")
		results = load_documents_from_json(path=path, dt="Test Doctype", logger=mock_logger)

		self.assertIsNone(results)
		mock_logger.error.assert_called_once()

	def test_load_documents_from_json_empty_file(self):
		"""Test loading from empty file."""
		mock_logger = MagicMock()

		with (
			patch("os.path.exists", return_value=True),
			patch("frappe.get_app_path", return_value="/test/path/file.json"),
			patch("vir_conto.util.read_doc_from_file", return_value=None),
		):
			result = load_documents_from_json("test_file.json", "Test DocType", mock_logger)

			self.assertIsNone(result)
			mock_logger.warning.assert_called_once()

	def test_load_documents_from_json_exception(self):
		"""Test loading from file with exception."""
		mock_logger = MagicMock()

		with (
			patch("os.path.exists", return_value=True),
			patch("frappe.get_app_path", return_value="/test/path/file.json"),
			patch("vir_conto.util.read_doc_from_file", side_effect=Exception("Test error")),
		):
			result = load_documents_from_json("test_file.json", "Test DocType", mock_logger)

			self.assertIsNone(result)
			mock_logger.exception.assert_called_once()

	def test_remove_old_workbooks(self):
		"""Test removal of old workbooks."""
		mock_logger = MagicMock()
		import_workbooks = [CustomInsightsWorkbook(wb) for wb in self.sample_workbook_data]

		# Mock existing workbook that should be removed
		old_workbook_data = {
			"doctype": "Insights Workbook",
			"name": "2",
			"title": "Old Workbook",
			"vir_id": "vir-old-workbook",
			"is_default": 1,
			"queries": "[]",
			"charts": "[]",
			"dashboards": "[]",
		}

		old_workbooks = frappe.get_doc(old_workbook_data)
		with (
			patch("frappe.db.get_all", return_value=[old_workbooks]),
			patch("frappe.get_doc") as mock_get_doc,
		):
			mock_doc = MagicMock()
			mock_get_doc.return_value = mock_doc

			_remove_old_workbooks(import_workbooks, mock_logger)

			mock_doc.delete.assert_called_once()

	def test_create_new_workbooks(self):
		"""Test creation of new workbooks."""
		mock_logger = MagicMock()
		import_workbooks = [CustomInsightsWorkbook(wb) for wb in self.sample_workbook_data]

		with patch("frappe.db.exists", return_value=False), patch("frappe.get_doc") as mock_get_doc:
			mock_doc = MagicMock()
			mock_get_doc.return_value = mock_doc

			_create_new_workbooks(import_workbooks, mock_logger)

			# Should be called twice for each workbook
			self.assertEqual(mock_get_doc.call_count, 2)
			self.assertEqual(mock_doc.insert.call_count, 2)

	def test_create_new_workbooks_already_exists(self):
		"""Test creation when workbooks already exist."""
		mock_logger = MagicMock()
		import_workbooks = [CustomInsightsWorkbook(wb) for wb in self.sample_workbook_data]

		with patch("frappe.db.exists", return_value=True), patch("frappe.get_doc") as mock_get_doc:
			_create_new_workbooks(import_workbooks, mock_logger)

			# Should not create any workbooks
			mock_get_doc.assert_not_called()

	def test_create_workbook_lookup_success(self):
		"""Test successful creation of workbook lookup table.

		The newly created Workbooks with ID: 1, 2 should match with the sample ID: 3, 5
		by comparing their 'vir_id'
		"""
		mock_logger = MagicMock()
		import_workbooks = [CustomInsightsWorkbook(wb) for wb in self.sample_workbook_data]

		existing_workbook_data = [
			{
				"doctype": "Insights Workbook",
				"name": "1",
				"title": "_Test Workbook 1",
				"vir_id": "vir-test-workbook-1",
				"is_default": 1,
				"queries": "[]",
				"charts": "[]",
				"dashboards": "[]",
			},
			{
				"doctype": "Insights Workbook",
				"name": "2",
				"title": "_Test Workbook 2",
				"vir_id": "vir-test-workbook-2",
				"is_default": 1,
				"queries": "[]",
				"charts": "[]",
				"dashboards": "[]",
			},
		]

		existing_workbooks = [CustomInsightsWorkbook(wb) for wb in existing_workbook_data]

		with (
			patch("frappe.get_all", return_value=existing_workbooks),
			patch("vir_conto.util._configure_workbook_access") as mock_configure,
		):
			results = _create_workbook_lookup(import_workbooks, mock_logger)

			self.assertIsNotNone(results)
			self.assertEqual(len(results), 2)
			self.assertEqual(results.get(9998)["new_id"], "1")
			self.assertEqual(results.get(9999)["new_id"], "2")
			self.assertEqual(mock_configure.call_count, 2)

	def test_create_workbook_lookup_exception(self):
		"""Test workbook lookup creation with exception."""
		mock_logger = MagicMock()
		import_workbooks = [CustomInsightsWorkbook(wb) for wb in self.sample_workbook_data]

		with patch("frappe.get_all", side_effect=Exception("Database error")):
			result = _create_workbook_lookup(import_workbooks, mock_logger)

			self.assertIsNone(result)
			mock_logger.exception.assert_called_once()

	def test_clean_existing_records(self):
		"""Test cleaning of existing records."""
		mock_logger = MagicMock()
		workbooks = ["wb-1", "wb-2"]
		# "Insights Query v3", "Insights Chart v3", "Insights Dashboard v3"

		with patch("frappe.db.delete") as mock_delete:
			_clean_existing_records(workbooks, mock_logger)

			# Should be called for each doctype
			self.assertEqual(mock_delete.call_count, 3)
			mock_delete.assert_any_call("Insights Query v3", filters={"workbook": ["in", workbooks]})
			mock_delete.assert_any_call("Insights Chart v3", filters={"workbook": ["in", workbooks]})
			mock_delete.assert_any_call("Insights Dashboard v3", filters={"workbook": ["in", workbooks]})

	def test_clean_existing_records_exception(self):
		"""Test cleaning records with database exception."""
		mock_logger = MagicMock()
		workbooks = ["wb-1"]

		with patch("frappe.db.delete", side_effect=Exception("Delete failed")):
			_clean_existing_records(workbooks, mock_logger)

			mock_logger.error.assert_called_once()

	def test_import_charts_success(self):
		"""Test successful import of charts."""
		mock_logger = MagicMock()
		workbook_lookup = {3: WorkbookInfo({"new_id": "1", "vir_id": "vir-test-workbook-1"})}
		doctypes = ["Insights Query v3"]

		with patch("vir_conto.util.load_documents_from_json") as mock_load:
			mock_doc = MagicMock()
			mock_doc.doctype = "Insights Query v3"
			mock_doc.workbook = 3
			mock_doc.name = "test-query-1"
			mock_load.return_value = [mock_doc]

			_import_charts(workbook_lookup, os.path.join("vir_conto", "tests"), doctypes, mock_logger)

			mock_load.assert_called_once_with(
				os.path.join("vir_conto", "tests", "insights_query_v3.json"), "Insights Query v3", mock_logger
			)
			mock_doc.insert.assert_called_once_with(ignore_links=True, set_name="test-query-1")
			self.assertEqual(mock_doc.workbook, "1")

	def test_import_charts_no_workbook_mapping(self):
		"""Test import charts when no workbook mapping found."""
		mock_logger = MagicMock()
		workbook_lookup = {1: WorkbookInfo({"new_id": "new-wb-1", "vir_id": "vir-test-workbook-1"})}
		doctypes = ["Insights Query v3"]
		base_path = os.path.join(frappe.get_app_path("vir_conto"), "tests")

		with (
			patch("vir_conto.util.load_documents_from_json") as mock_load,
			patch("frappe.scrub", return_value="insights_query_v3"),
		):
			mock_doc = MagicMock()
			mock_doc.workbook = 9998  # Non-existent workbook ID
			mock_doc.name = "test-query-1"
			mock_load.return_value = [mock_doc]

			_import_charts(workbook_lookup, base_path, doctypes, mock_logger)

			# Should log warning and not insert
			mock_logger.warning.assert_called_once()
			mock_doc.insert.assert_not_called()

	def test_import_charts_no_docs_found(self):
		"""Test import charts when no documents found."""
		mock_logger = MagicMock()
		workbook_lookup = {1: WorkbookInfo({"new_id": "new-wb-1", "vir_id": "vir-test-workbook-1"})}
		doctypes = ["Insights Query v3"]
		base_path = os.path.join(frappe.get_app_path("vir_conto"), "tests")

		with (
			patch("vir_conto.util.load_documents_from_json") as mock_load,
			patch("frappe.scrub", return_value="insights_query_v3"),
		):
			mock_load.return_value = None

			_import_charts(workbook_lookup, base_path, doctypes, mock_logger)

			mock_logger.warning.assert_called_once()

	def test_import_charts_insert_exception(self):
		"""Test import charts with insert exception."""
		mock_logger = MagicMock()
		workbook_lookup = {1: WorkbookInfo({"new_id": "new-wb-1", "vir_id": "vir-test-workbook-1"})}
		doctypes = ["Insights Query v3"]
		base_path = os.path.join(frappe.get_app_path("vir_conto"), "tests")

		with (
			patch("vir_conto.util.load_documents_from_json") as mock_load,
			patch("frappe.scrub", return_value="insights_query_v3"),
		):
			mock_doc = MagicMock()
			mock_doc.workbook = 1
			mock_doc.name = "test-query-1"
			mock_doc.insert.side_effect = Exception("Insert failed")
			mock_load.return_value = [mock_doc]

			_import_charts(workbook_lookup, base_path, doctypes, mock_logger)

			mock_logger.error.assert_called_once()

	def test_integration_sync_with_real_file_structure(self):
		"""Integration test using real JSON test files and database verification."""
		# Clean up any existing test data first
		frappe.db.delete("Insights Dashboard v3", {"title": ["like", "_Test%"]})
		frappe.db.delete("Insights Chart v3", {"title": ["like", "_Test%"]})
		frappe.db.delete("Insights Query v3", {"title": ["like", "_Test%"]})
		frappe.db.delete("Insights Workbook", {"title": ["like", "_Test%"]})
		frappe.db.commit()

		# Mock the file paths to use test directory instead of charts directory
		test_path = os.path.join(frappe.get_app_path("vir_conto"), "tests")

		# Execute the sync function with real test files
		sync_default_charts(base_path=test_path)

		# Verify workbooks were created in database
		workbooks = frappe.get_all(
			"Insights Workbook",
			filters={"is_default": 1, "title": ["like", "_Test%"]},
			fields=["name", "title", "vir_id", "is_default"],
		)

		self.assertGreaterEqual(len(workbooks), 2, "Expected at least 2 test workbooks to be created")

		# Check that workbook with title starting with "_" exists
		default_workbook = next((wb for wb in workbooks if wb.title.startswith("_Test")), None)
		self.assertIsNotNone(default_workbook, "Expected workbook with title starting with '_Test' to exist")

		# Verify queries were created and linked to correct workbook
		queries = frappe.get_all(
			"Insights Query v3", filters={"title": ["like", "_Test%"]}, fields=["name", "title", "workbook"]
		)

		self.assertGreaterEqual(len(queries), 1, "Expected at least 1 test query to be created")

		# Verify the query is linked to an existing workbook
		query_workbook_names = [q.workbook for q in queries]
		workbook_names = [str(wb.name) for wb in workbooks]

		for qwb_name in query_workbook_names:
			self.assertIn(qwb_name, workbook_names, f"Query workbook {qwb_name} should match an existing workbook")

		# Verify charts were created and linked correctly
		charts = frappe.get_all(
			"Insights Chart v3",
			filters={"title": ["like", "_Test%"]},
			fields=["name", "title", "workbook", "chart_type"],
		)

		self.assertGreaterEqual(len(charts), 1, "Expected at least 1 test chart to be created")

		# Verify chart workbook linkage
		chart_workbook_names = [c.workbook for c in charts]
		for cwb_name in chart_workbook_names:
			self.assertIn(cwb_name, workbook_names, f"Chart workbook {cwb_name} should match an existing workbook")

		# Verify dashboards were created and linked correctly
		dashboards = frappe.get_all(
			"Insights Dashboard v3",
			filters={"title": ["like", "_Test%"]},
			fields=["name", "title", "workbook"],
		)

		self.assertGreaterEqual(len(dashboards), 1, "Expected at least 1 test dashboard to be created")

		# Verify dashboard workbook linkage
		dashboard_workbook_names = [d.workbook for d in dashboards]
		for dwb_name in dashboard_workbook_names:
			self.assertIn(dwb_name, workbook_names, f"Dashboard workbook {dwb_name} should match an existing workbook")

		# Verify workbook ID mapping worked correctly
		# The test JSON files use workbook ID 9998, which should be mapped to actual workbook names
		test_linked_items = queries + charts + dashboards
		self.assertGreater(len(test_linked_items), 0, "Expected some items to be linked to workbooks")

		# All linked items should have valid workbook references (not the original ID 9998)
		for item in test_linked_items:
			self.assertNotEqual(item.workbook, 9998, f"Item {item.name} should not reference original workbook ID 9998")
			self.assertIsNotNone(item.workbook, f"Item {item.name} should have a valid workbook reference")

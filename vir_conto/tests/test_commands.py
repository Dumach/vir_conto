import glob
import os
import unittest
from unittest.mock import MagicMock, Mock, patch

import frappe
from frappe.modules.import_file import read_doc_from_file

from vir_conto.commands import export_default_charts
from vir_conto.overrides.insights_workbook import CustomInsightsWorkbook


class TestCommands(unittest.TestCase):
	"""Test suite for command.py module functions."""

	@classmethod
	def setUpClass(cls):
		"""Set up test class with required test records."""
		frappe.set_user("Administrator")

	def setUp(self):
		"""Set up test data before each test."""
		# Mock environment variables
		self.import_path = frappe.get_app_path("vir_conto", "tests", "test_imports")
		self.export_path = frappe.get_app_path("vir_conto", "tests", "test_exports")

		from vir_conto.util import sync_default_charts

		print("Importing default Charts")
		sync_default_charts()

	def tearDown(self):
		"""Clean up after each test."""
		frappe.db.delete("Insights Dashboard v3")
		frappe.db.delete("Insights Chart v3")
		frappe.db.delete("Insights Query v3")
		frappe.db.delete("Insights Workbook")

		# Remove output files
		for filename in os.listdir(self.export_path):
			file_path = os.path.join(self.export_path, filename)
			if os.path.isfile(file_path):
				os.remove(file_path)

	def test_export_default_charts_success(self):
		"""Test successful export of default charts"""
		_ = export_default_charts(self.export_path)

		# Count files located in test/test_exports
		count = len(glob.glob(pathname="*.json", root_dir=self.export_path))
		self.assertEqual(
			count, 5, "Count of expected files are 4, which are (insights_chart_v3/dashboard_v3/query_v3/workbook.json"
		)

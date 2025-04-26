# Copyright (c) 2025, Alex Nagy and Contributors
# See license.txt

import os.path
import shutil
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase
import frappe.utils

from .data_packet import clear_old_packets, datapacket


def create_datapacket(file_name: str):
	doc = frappe.get_doc(
		{
			"doctype": "data-packet",
			"file_name": file_name,
		}
	)

	if not frappe.db.exists("data-packet", file_name):
		doc.insert()


class Testdatapacket(FrappeTestCase):
	def test_datapacket_return_correct_paths(self):
		# Mock data
		file_name = "TEST-0001"
		create_datapacket(file_name)

		doc: datapacket = frappe.get_doc("data-packet", file_name)

		self.assertEqual(doc.get_file_url(), f"{frappe.get_site_path()}/private/files/{file_name}.LZH")
		self.assertEqual(
			doc.get_extraction_dir(), f"{frappe.get_site_path()}/private/files/storage/{file_name}"
		)

	def test_clear_old_packets(self):
		frappe.set_user("Administrator")

		# Create mock data-packet
		file_name = "TEST-0001"
		create_datapacket(file_name)

		doc: datapacket = frappe.get_doc("data-packet", file_name)
		frappe.db.set_value(
			"data-packet", file_name, "creation", frappe.utils.nowdate(), update_modified=False
		)
		frappe.db.commit()
		extraction_dir = doc.get_extraction_dir()

		# Copy mock file
		src_path = "../apps/vir_conto/vir_conto/vir_conto/doctype/data_packet/TEST-0001.LZH"
		dest_path = os.path.join(extraction_dir, file_name + ".LZH")

		if not os.path.exists(extraction_dir):
			os.makedirs(extraction_dir)

		file = Path(dest_path)
		shutil.copy(src_path, dest_path)

		# Call cleanup to check if deletes younger than 30 day
		clear_old_packets()
		# Check if data-packet and file exist
		self.assertIsNotNone(frappe.db.exists("data-packet", file_name))
		self.assertTrue(file.exists())

		# Change creation_date
		frappe.db.set_value("data-packet", file_name, "creation", "2025.03.25", update_modified=False)
		frappe.db.commit()
		# Call cleanup function
		clear_old_packets()
		# Check if data-packet and file successfully deleted
		self.assertIsNone(frappe.db.exists("data-packet", file_name))
		self.assertFalse(file.exists())

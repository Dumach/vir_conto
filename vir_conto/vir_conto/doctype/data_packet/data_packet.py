# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import os
import zipfile

import frappe
from frappe.model.document import Document

from vir_conto.util import process_dbf


class datapacket(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		file: DF.Attach | None
		file_name: DF.Data | None
		is_processed: DF.Check
	# end: auto-generated types

	def after_insert(self):
		self.import_data()

	def import_data(self):
		file_url = os.path.join(frappe.get_site_path("private", "files"), str(self.file_name) + ".LZH")
		extraction_dir = os.path.join(
			frappe.get_site_path("private", "files", "storage"), str(self.file_name)
		)

		# Create the extraction directory if it doesn't exist
		if not os.path.exists(extraction_dir):
			os.makedirs(extraction_dir)

		# Open the zip file
		with zipfile.ZipFile(file_url, "r") as zip_ref:
			# Extract all the contents into the specified directory
			zip_ref.extractall(extraction_dir)

		# Process dbf files
		encoding = "cp1250"
		doctypes = frappe.db.get_all(
			"primary-key",
			fields=["name", "is_updateable", "import_order"],
			filters={"is_enabled": True},
			order_by="import_order",
		)

		for doctype in doctypes:
			dbf_file = os.path.join(extraction_dir, doctype.name + ".dbf")

			if not doctype.is_updateable:
				# clean all entries because the whole dataset is sent
				frappe.db.delete(doctype.name)

				process_dbf(dbf_file, doctype.name, encoding)

		frappe.db.commit()
		self.is_processed = True

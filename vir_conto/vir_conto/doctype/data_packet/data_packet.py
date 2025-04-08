# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import os
import zipfile

import dbf
import frappe
from frappe.model.document import Document


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
		# TODO:
		#  - get file from storage
		#  - unzip
		#  - update or create doctype

		file_url = os.path.join(frappe.get_site_path("private", "files"), str(self.file_name) + ".LZH")
		extraction_dir = os.path.join(
			frappe.get_site_path("private", "files", "storage"), str(self.file_name)
		)

		# Create the extraction directory if it doesn't exist
		if not os.path.exists(extraction_dir):
			print(extraction_dir)
			os.makedirs(extraction_dir)

		# Open the zip file
		with zipfile.ZipFile(file_url, "r") as zip_ref:
			# Extract all the contents into the specified directory
			zip_ref.extractall(extraction_dir)

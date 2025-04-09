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
		#  - update or create doctype
		#  - change naming setting on: vir_csop, vir_bolt

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

		# Process dbf files
		encoding = "cp1250"

		# tfocsop
		doctype = "tfocsop"
		dbf_file = os.path.join(extraction_dir, doctype + ".dbf")
		process_dbf(dbf_file, doctype, encoding)

		# tcsop
		doctype = "tcsop"
		dbf_file = os.path.join(extraction_dir, doctype + ".dbf")
		process_dbf(dbf_file, doctype, encoding)

		# raktnev
		doctype = "raktnev"
		dbf_file = os.path.join(extraction_dir, doctype + ".dbf")
		process_dbf(dbf_file, doctype, encoding)

		# torzs
		doctype = "torzs"
		dbf_file = os.path.join(extraction_dir, doctype + ".dbf")
		process_dbf(dbf_file, doctype, encoding)

		# vir_csop
		doctype = "vir_csop"
		dbf_file = os.path.join(extraction_dir, doctype + ".dbf")
		process_dbf(dbf_file, doctype, encoding)

		# vir_bolt
		doctype = "vir_bolt"
		dbf_file = os.path.join(extraction_dir, doctype + ".dbf")
		process_dbf(dbf_file, doctype, encoding)

		self.is_processed = True


def process_dbf(dbf_file: str, doctype: str, encoding: str):
	try:
		table = dbf.Table(dbf_file, codepage=encoding, on_disk=True)
		field_names = table.field_names
		table.open()

		for record in table:
			row = {}
			print(record)
			for field_name in field_names:
				field_info = table.field_info(field_name)
				# Strings are not trimmed by default
				if field_info.py_type is str:
					value = record[field_name].strip()
				else:
					value = record[field_name]

				row[field_name.lower()] = value
			row["doctype"] = doctype
			insert_db(row)

	except dbf.exceptions.DbfError as e:
		print(e.message)


def insert_db(row):
	# create a new document or update existing
	doctype = row["doctype"]
	pkey = ""
	match doctype:
		case "tfocsop":
			pkey = "kod"
		case "tcsop":
			pkey = "kod"
		case "raktnev":
			pkey = "rkod"
		case "torzs":
			pkey = "f_kod"
		case "vir_csop":
			pkey = "kod"
		case "vir_bolt":
			pkey = "kod"

	if not frappe.db.exists(doctype, row[pkey]):
		# create new
		new_doc = frappe.get_doc(row)
		new_doc.insert()
	else:
		# update
		_doc = frappe.get_doc(doctype, row[pkey])
		_doc.update(row)
		_doc.save()

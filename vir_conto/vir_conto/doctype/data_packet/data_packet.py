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
		#  - handle torolt.dbf before importing
		#  - torolt: tip + kod -> what needs to be removed from db

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
		doctypes = PRIMARY_KEYS.keys()
		for doctype in doctypes:
			dbf_file = os.path.join(extraction_dir, doctype + ".dbf")
			process_dbf(dbf_file, doctype, encoding)

		self.is_processed = True


PRIMARY_KEYS = {
	"tfocsop": "kod",
	"tcsop": "kod",
	"raktnev": "rkod",
	"torzs": "f_kod",
	"vir_csop": ["tipus", "csop", "rkod", "datum"],
	"vir_bolt": ["rkod", "datum"],
}


def process_dbf(dbf_file: str, doctype: str, encoding: str):
	try:
		table = dbf.Table(dbf_file, codepage=encoding, on_disk=True)
		field_names = table.field_names
		table.open()

		for record in table:
			row = {}
			for field_name in field_names:
				field_info = table.field_info(field_name)
				if field_info.py_type is str:
					# Strings are not trimmed by default
					value = str(record[field_name]).strip()
				else:
					value = record[field_name]
				row[field_name.lower()] = value
			row["doctype"] = doctype
			insert_into_db(doctype, row)

	except dbf.exceptions.DbfError as e:
		print(e.message)


def insert_into_db(doctype: str, row):
	# Selects the primary key for the appropriate doctype
	pkey = PRIMARY_KEYS[doctype]
	pkey_value = ""

	if isinstance(pkey, list):
		for key in pkey:
			pkey_value += row[key] + "/"
		pkey_value = pkey_value.rstrip("/")
	else:
		pkey_value = row[pkey]

	if not frappe.db.exists(doctype, pkey_value):
		# create new
		new_doc = frappe.get_doc(row)
		new_doc.insert()
	else:
		# update
		_doc = frappe.get_doc(doctype, pkey_value)
		_doc.update(row)
		_doc.save()

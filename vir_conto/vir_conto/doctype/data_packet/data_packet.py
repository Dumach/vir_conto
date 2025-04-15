# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import os
import zipfile

import dbf
import frappe
from frappe.model.document import Document

from vir_conto.vir_conto.doctype.primary_key.primary_key import primarykey


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

			if doctype == "torolt":
				remove_from_db(row)
			else:
				insert_into_db(row)

	except dbf.exceptions.DbfError as e:
		print(e.message)


def remove_from_db(row):
	pass
	# frappe.db.get_all("primary-key", filters={'type': ['=', 'TERM']})
	# TODO:
	# - may need to implement composite keys
	# frappe.delete_doc(doctype, row["kod"])
	# 	 if tip='TERM' then
	#     if findkij(dmf.tblTermek,kod) then abl_term.termek_torol(True);
	#    if tip='PARTN' then
	#     if findkij(dmf.tblPartner,kod) then db_muv('D',dmf.tblPartner);
	#    if tip='TELEP' then
	#     if findkij(dmf.tblTelep,kod) then db_muv('D',dmf.tblTelep);
	#    if tip='GVKOD' then
	#     if findkij(dmf.tblGyujtvk,kod) then db_muv('D',dmf.tblGyujtvk);
	#    if tip='ARAK' then


def get_name(row: dict) -> str:
	# Selects the primary key for the appropriate doctype
	pkey: primarykey = frappe.get_doc("primary-key", row["doctype"]).cconto_pkey
	pkey_list = pkey.split(",")
	name = ""

	if isinstance(pkey_list, list) and len(pkey_list) > 1:
		for key in pkey_list:
			name += row[key] + "/"
		name = name.rstrip("/")
	else:
		name = row[pkey]

	return name


def insert_into_db(row: dict) -> None:
	pkey = get_name(row)
	doctype = row["doctype"]

	if not frappe.db.exists(doctype, pkey):
		# create new
		new_doc = frappe.get_doc(row)
		new_doc.insert()
	else:
		# update
		old_doc = frappe.get_doc(doctype, pkey)
		old_doc.update(row)
		old_doc.save()

# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import os
import shutil
import zipfile

import dbf
import frappe
import frappe.utils
from frappe.model.document import Document

from vir_conto.vir_conto.doctype.primary_key.primary_key import PrimaryKey


class DataPacket(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		file_name: DF.Data | None
		processed: DF.Check
	# end: auto-generated types

	def get_file_url(self) -> str:
		return os.path.join(frappe.get_site_path("private", "files"), str(self.file_name) + ".LZH")

	def get_extraction_dir(self) -> str:
		return os.path.join(frappe.get_site_path("private", "files", "storage"), str(self.file_name) + ".LZH")

	def after_insert(self) -> None:
		frappe.enqueue_doc("Data Packet", self.name, method="import_data")

	@frappe.whitelist()
	def import_data(self) -> None:
		"""
		Import logic for Conto export files. It extracts than processes the debase files.
		"""
		file_url = self.get_file_url()
		extraction_dir = self.get_extraction_dir()

		# Create the extraction directory if it doesn't exist
		if not os.path.exists(extraction_dir):
			os.makedirs(extraction_dir)

		# Open the zip file
		with zipfile.ZipFile(file_url, "r") as zip_ref:
			# Extract all the contents into the specified directory
			zip_ref.extractall(extraction_dir)

		# Process dbf files
		encoding = "cp1250"
		doctypes = frappe.db.get_list(
			"Primary Key",
			fields=["name", "updateable", "import_order"],
			filters={"enabled": True},
			order_by="import_order",
		)

		for doctype in doctypes:
			dbf_file = os.path.join(extraction_dir, doctype.name + ".dbf")

			if not doctype.updateable:
				# clean all entries because the whole dataset is sent
				frappe.db.delete(doctype.name)

			process_dbf(dbf_file, doctype.name, encoding)

		self.processed = True
		self.save()
		frappe.db.commit()  # nosemgrep


def process_dbf(dbf_file: str, doctype: str, encoding: str) -> None:
	"""Method for processing a DBase file.

	Args:
	        dbf_file: Source path of debase file.
	        doctype: What doctype it needs to create.
	        encoding: Debase file encoded in.
	"""
	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	logger.setLevel("INFO")

	try:
		table = dbf.Table(dbf_file, codepage=encoding, on_disk=True)
		table.open()

		field_names = table.field_names
		field_infos = {field_name: table.field_info(field_name) for field_name in field_names}
		for record in table:
			row = {}
			for field_name in field_names:
				# Trim strings
				if field_infos[field_name].py_type is str:
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
		logger.exception(e.message)
	except Exception as e:
		logger.exception(str(e))


def remove_from_db(row):
	pkey_info = frappe.get_list("Primary Key", fields=["*"], filters={"type": row["tipus"]})
	row["doctype"] = pkey_info.get("frappe_name")

	frappe.delete_doc_if_exists(row["doctype"], get_name(row))
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
	"""
	Method for creating / accessing a primary key for Conto doctypes.

	Args:
	        row: Data row must contain a 'doctype' field in order to create the key.

	Returns:
	        Returns the correct primary key as a string.
	"""
	# Selects the primary key for the correct doctype
	pkey: str = frappe.get_doc("Primary Key", row["doctype"]).conto_primary_key
	pkey_list = pkey.split(",")
	name = ""

	# Handling composite (multiple field) key creation
	if isinstance(pkey_list, list) and len(pkey_list) > 1:
		for key in pkey_list:
			name += row[key] + "/"
		name = name.rstrip("/")
	else:
		name = row[pkey]

	return name


def insert_into_db(row: dict) -> None:
	"""
	Inserts a key:value pair row into Frappe DB.

	Args
	        row: Data row must contain a 'doctype' field in order to create a new Frappe document.
	"""
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


def import_new_packets() -> int:
	"""Job to import new packets that is not processed, coming from Conto."""
	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	logger.setLevel("INFO")

	# Health check midnight every day
	hour = int(frappe.utils.nowtime().split(":")[0])
	if hour == 0:
		logger.info("Background job is alive")

	packets = frappe.db.get_list("Data Packet", filters={"processed": False}, order_by="creation", pluck="name")

	if len(packets) < 1:
		return 0

	logger.info("Beginning to import new packets")
	try:
		for p in packets:
			frappe.enqueue_doc("Data Packet", p, method="import_data")
	except Exception as e:
		logger.error(e)

	logger.info(f"{len(packets)} packet(s) imported")
	return len(packets)


def clear_old_packets() -> None:
	"""
	Clearing older than a month (>30 day) packets and files.

	In order to prevent exploding database sizes.
	"""

	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	logger.setLevel("INFO")

	logger.info("Beginning to clean old packets")
	max_date = frappe.utils.add_days(frappe.utils.getdate(), -30)

	try:
		old_packets = frappe.db.get_all("Data Packet", {"creation": ["<", max_date]}, pluck="name")

		# Remove from `tabFile`
		before_delete = frappe.db.count("File", filters={"file_name": ["in", old_packets]})
		frappe.db.delete(
			"File",
			filters={"creation": ["<", max_date], "file_name": ["in", old_packets]},
		)
		after_delete = frappe.db.count("File", filters={"file_name": ["in", old_packets]})
		logger.info(f"Removed {before_delete - after_delete} old file(s)")

		# Remove from `tabData Packet` and filesystem
		before_delete = frappe.db.count("Data Packet")
		for p in old_packets:
			packet: DataPacket = frappe.get_doc("Data Packet", p)
			shutil.rmtree(packet.get_extraction_dir())
			os.remove(packet.get_file_url())
			packet.delete()
		after_delete = frappe.db.count("Data Packet")
		logger.info(f"Removed {before_delete - after_delete} old packet(s)")
	except Exception as e:
		logger.exception(e)

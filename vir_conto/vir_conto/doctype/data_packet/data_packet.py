# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import os
import shutil
import zipfile
from typing import Literal

import dbf
import frappe
import frappe.utils
from frappe.model.document import Document


class DataPacket(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		file_name: DF.Data | None
		processed: DF.Check
	# end: auto-generated types

	def get_file_path(self) -> str:
		return frappe.get_site_path("private", "files", self.file_name)

	def get_extraction_dir(self) -> str:
		return frappe.get_site_path("private", "files", "storage", self.file_name)

	def after_insert(self) -> None:
		frappe.enqueue_doc("Data Packet", self.name, method="import_packet")

	@frappe.whitelist()
	def import_packet(self, verbose: Literal["console", "web"] | None = None):
		"""Import logic for Conto export files. It extracts than processes the DBase files.

		Args:
		        verbose (Literal[&quot;console&quot;, &quot;web&quot;] | None): Show progress on console or web. Defaults to None.
		"""
		extraction_dir = self.get_extraction_dir()

		# Create the extraction directory if Trueit doesn't exist
		if not os.path.exists(extraction_dir):
			os.makedirs(extraction_dir)

		# Open the zip file
		with zipfile.ZipFile(self.get_file_path(), "r") as zip_ref:
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

		logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
		logger.setLevel("INFO")
		logger.info(f"Beginning to import Data Packet: {self.name}")

		for idx, doctype in enumerate(doctypes):
			if verbose == "console":
				frappe.utils.update_progress_bar(f"Importing {doctype.name} doctype", idx, len(doctypes))
			if verbose == "web":
				frappe.publish_progress(
					(idx / len(doctypes)) * 100, title="Importing", description=f"Processing {doctype.name} doctype"
				)

			dbf_file = os.path.join(extraction_dir, doctype.name + ".dbf")
			if not doctype.updateable:
				# clean all entries because the whole dataset is sent
				frappe.db.delete(doctype.name)
			process_dbf(dbf_file, doctype.name, encoding)
			frappe.db.commit()  # nosemgrep

		self.processed = True
		self.save()


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

		logger.info(f"Importing {len(table):n} records from {dbf_file}")

		fields = table.field_names
		field_infos = {field_name: table.field_info(field_name) for field_name in fields}
		for record in table:
			row = {}

			for field in fields:
				# Trim strings
				if field_infos[field].py_type is str:
					value = str(record[field]).strip()
				else:
					value = record[field]
				row[field.lower()] = value

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
	"""Method for removing an Item from Vir-Conto.

	Args:
	        row (_type_): A DBase record, that contains the TIPUS field
	"""
	# Get the doctype, that is associated with the TIPUS parameter from C-Conto
	doctype = frappe.db.get_value("Primary Key", {"type": row["tipus"]}, "frappe_name", cache=True)
	frappe.delete_doc_if_exists(doctype, get_name(row))

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
	        str: The correct primary key as a string.
	"""
	# Selects the primary key for the correct doctype
	primary_keys = frappe.db.get_value(
		"Primary Key", filters={"name": row["doctype"]}, fieldname="conto_primary_key", cache=True
	)
	field_list = primary_keys.split(",")
	result = ""

	# Handling composite (multiple field) key creation
	if isinstance(field_list, list) and len(field_list) > 1:
		for key in field_list:
			result += row[key] + "/"
		result = result.rstrip("/")
	else:
		result = row[primary_keys]

	return result


def insert_into_db(row: dict) -> None:
	"""
	Inserts a row into Frappe DB.

	Args
	        row: Data row must contain a 'doctype' field in order to create a new Frappe document.
	"""
	docname = get_name(row)
	doctype = row["doctype"]

	if not frappe.db.exists(doctype, docname):
		# create new
		new_doc = frappe.get_doc(row)
		new_doc.insert()
	else:
		# update
		old_doc = frappe.get_doc(doctype, docname)
		old_doc.update(row)
		old_doc.save()


def import_new_packets() -> int:
	"""Job to import new packets.

	Returns:
	        int: The number of packages imported.
	"""

	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	logger.setLevel("INFO")
	packets: list[str] = frappe.db.get_list(
		"Data Packet", filters={"processed": False}, order_by="creation", pluck="name"
	)

	if len(packets) < 1:
		return 0

	logger.info("Beginning to import new packets")
	try:
		for p in packets:
			frappe.enqueue_doc("Data Packet", name=p, method="import_packet")
	except Exception as e:
		logger.error(e)

	logger.info(f"{len(packets)} packet(s) imported")
	return len(packets)


def clear_old_packets() -> None:
	"""
	Clearing older than a month (>30 day) packets and files.

	In order to save space on disk.
	"""

	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	logger.setLevel("INFO")

	logger.info("Beginning to clean old packets")
	max_date = frappe.utils.add_days(frappe.utils.getdate(), -30)

	try:
		old_packets: list[str] = frappe.db.get_list("Data Packet", {"creation": ["<", max_date]}, pluck="name")

		# Remove from File doctype
		before_delete = frappe.db.count("File", filters={"file_name": ["in", old_packets]})

		frappe.db.delete(
			"File",
			filters={"creation": ["<", max_date], "file_name": ["in", old_packets]},
		)

		after_delete = frappe.db.count("File", filters={"file_name": ["in", old_packets]})
		logger.info(f"Removed {before_delete - after_delete} old file(s)")

		# Remove from Data Packet doctype and filesystem
		before_delete = frappe.db.count("Data Packet")

		for p in old_packets:
			packet: DataPacket = frappe.get_doc("Data Packet", p)
			shutil.rmtree(packet.get_extraction_dir())  # extracted contents
			os.remove(packet.get_file_path())  # archive file
			packet.delete()

		after_delete = frappe.db.count("Data Packet")
		logger.info(f"Removed {before_delete - after_delete} old packet(s)")
	except Exception as e:
		logger.exception(e)

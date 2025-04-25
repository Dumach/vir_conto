# Copyright (c) 2025, Alex Nagy and contributors
# For license information, please see license.txt

import os
import zipfile

import frappe
import frappe.utils
import frappe.utils.logger
from frappe.model.document import Document

from vir_conto.util import process_dbf


class datapacket(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		file_name: DF.Data | None
		is_processed: DF.Check
	# end: auto-generated types

	def get_file_url(self) -> str:
		return os.path.join(frappe.get_site_path("private", "files"), str(self.file_name) + ".LZH")

	def get_extraction_dir(self) -> str:
		return os.path.join(frappe.get_site_path("private", "files", "storage"), str(self.file_name))

	def import_data(self) -> None:
		"""
		Import logic for CConto export files. It extracts than processes the debase files.
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

		self.is_processed = True
		self.save()
		frappe.db.commit()


def import_new_packets() -> None:
	"""Job to import new packets that is not processed, coming from Cconto"""
	frappe.utils.logger.set_log_level("INFO")
	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)

	# Health check midnight every day
	hour = int(frappe.utils.nowtime().split(":")[0])
	minute = int(frappe.utils.nowtime().split(":")[1])
	if hour == 0 and minute > 0 and minute < 5:
		logger.info("Background job is alive")

	packets = frappe.db.get_list(
		"data-packet", filters={"is_processed": False}, order_by="creation", pluck="name"
	)

	if len(packets) < 1:
		return

	logger.info("Beginning to import new packets")
	try:
		for p in packets:
			packet: datapacket = frappe.get_doc("data-packet", p)
			packet.import_data()
	except Exception as e:
		logger.error(e)
	logger.info(f"{len(packets)} packet(s) imported")


def clear_old_packets() -> None:
	"""
	Clearing older than a month (>30 day) packets and files.

	In order to prevent exploding database sizes.
	"""
	import shutil

	frappe.utils.logger.set_log_level("INFO")
	logger = frappe.logger("import", allow_site=True, file_count=5, max_size=250000)
	logger.info("Beginning to clean old packets")

	max_date = frappe.utils.add_days(frappe.utils.getdate(), -30)

	try:
		before_delete = frappe.db.count("data-packet")

		# Removing extracted packets from Storage
		old_packets = frappe.db.get_all("data-packet", {"creation": ["<", max_date]}, pluck="name")
		for p in old_packets:
			packet: datapacket = frappe.get_doc("datapacket", p)
			shutil.rmtree(packet.get_extraction_dir())

		# Removing data packet entries
		after_delete = frappe.db.count("data-packet")
		frappe.db.delete("data-packet", {"creation": ["<", max_date]})
		logger.info(f"Removed {before_delete - after_delete} old packet(s)")

		# Removing files from site/private
		before_delete = frappe.db.count("File")
		frappe.db.delete(
			"File",
			{"creation": ["<", max_date], "file_name": ["like", "%EI%.LZH"]},
		)
		after_delete = frappe.db.count("File")
		logger.info(f"Removed {before_delete - after_delete} old file(s)")
	except Exception as e:
		logger.error(e)

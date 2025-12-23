# Copyright (c) 2025, Alex Nagy and Contributors
# See license.txt

import os.path
import shutil
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import frappe
import frappe.utils

from vir_conto.vir_conto.doctype.data_packet.data_packet import (
	DataPacket,
	clear_old_packets,
	get_name,
	import_new_packets,
	insert_into_db,
	process_dbf,
	remove_from_db,
)


def create_datapacket(file_name: str):
	doc = frappe.get_doc(
		{
			"doctype": "Data Packet",
			"file_name": file_name,
			"processed": True,
		}
	)

	if not frappe.db.exists("Data Packet", file_name):
		doc.insert()


def copy_datapacket(data_packet: DataPacket, file_name: str) -> bool:
	# Copy mock file
	extraction_dir = data_packet.get_extraction_dir()
	try:
		if not os.path.exists(extraction_dir):
			os.makedirs(extraction_dir)

		src_path = "../apps/vir_conto/vir_conto/vir_conto/doctype/data_packet/TEST-0001.LZH"
		dest_path = os.path.join(frappe.get_site_path("private", "files"), file_name)
		shutil.copy(src_path, dest_path)
	except Exception as error:
		frappe.throw(str(error), type(error))
		return False

	return True


class TestDataPacket(unittest.TestCase):
	"""Test suite for Data Packet doctype."""

	@classmethod
	def setUpClass(cls):
		"""Set up test class with required test records."""
		frappe.set_user("Administrator")

	def setUp(self) -> None:
		"""Set up before each test"""
		self.dbf_table_mock = MagicMock()
		self.dbf_table_mock.field_names = ["id", "name"]
		self.dbf_table_mock.__iter__.return_value = [
			{"id": 1, "name": "Alice "},
			{"id": 2, "name": " Bob"},
		]
		self.dbf_table_mock.field_info.side_effect = lambda name: (
			MagicMock(py_type=int) if name == "id" else MagicMock(py_type=str)
		)

	def tearDown(self):
		"""Clean up after each test."""
		frappe.db.rollback()
		frappe.db.delete("Data Packet")

	def test_datapacket_return_correct_paths(self):
		"""
		Test if 'get_file_url' and 'get_extraction_dir' returns correct paths.
		"""
		# Create mock Data Packet
		file_name = "TEST-0001.ZIP"
		create_datapacket(file_name)
		doc: DataPacket = frappe.get_doc("Data Packet", file_name)

		# Execute function
		self.assertEqual(doc.get_file_path(), f"{frappe.get_site_path()}/private/files/{file_name}")
		self.assertEqual(doc.get_extraction_dir(), f"{frappe.get_site_path()}/private/files/storage/{file_name}")

	def test_get_name_return_correctly(self):
		"""
		Test to generate name field for Vir Conto doctypes when presented a document.

		Name is generated from Primary Key doctype.
		"""
		# Check with simple key
		test_row = {
			"kod": "901",
			"nev": "GÖNGYÖLEG",
			"rend": 0,
			"tarhely": "",
			"focsop": "200",
			"doctype": "tcsop",
		}
		self.assertEqual("901", get_name(test_row))

		# Check with composite key
		test_composite_row = {
			"rkod": "106",
			"rnev": "ZG Húsbolt",
			"datum": "2025.03.22",
			"ho": "03",
			"keszlet": 2029470.0,
			"nbesz_kp": 0.0,
			"bbesz_kp": 0.0,
			"nbesz_nkp": 0.0,
			"bbesz_nkp": 0.0,
			"nert_ossz": 449130.0,
			"bert_ossz": 510362.0,
			"vevok": 77,
			"kosara": 5833.0,
			"nszallrend": 0.0,
			"bszallrend": 0.0,
			"haszon": 134163.0,
			"hkulcs": 29.87,
			"neg_keszlm": -1577.0,
			"bert_eng": 1.0,
			"bsaj_felh": 0.0,
			"bselejt": 0.0,
			"doctype": "vir_bolt",
		}
		self.assertEqual("106/2025.03.22", get_name(test_composite_row))

	def test_import_insert_db(self):
		mock_data = {
			"kod": "901",
			"nev": "GÖNGYÖLEG",
			"rend": 0,
			"tarhely": "",
			"focsop": "200",
			"doctype": "tcsop",
		}
		mock_doc = MagicMock()

		with (
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.get_name"),
			patch("frappe.db.exists", return_value=False),
			patch("frappe.get_doc", return_value=mock_doc),
		):
			# Execute function
			insert_into_db(mock_data)
			mock_doc.insert.assert_called_once()

	def test_import_update_db(self):
		mock_data = {
			"kod": "901",
			"nev": "GÖNGYÖLEG",
			"rend": 0,
			"tarhely": "",
			"focsop": "200",
			"doctype": "tcsop",
		}
		mock_doc = MagicMock()

		with (
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.get_name"),
			patch("frappe.db.exists", return_value=True),
			patch("frappe.get_doc", return_value=mock_doc),
		):
			# Execute function
			insert_into_db(mock_data)
			mock_doc.update.assert_called_once()
			mock_doc.save.assert_called_once()

	def test_process_dbf_inserts_records(self):
		"""Test call insert_into_db, if doctype != 'torolt'."""
		with (
			patch("dbf.Table", return_value=self.dbf_table_mock),
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.insert_into_db") as mock_insert,
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.remove_from_db") as mock_remove,
			patch("frappe.logger") as _mock_logger,
		):
			# Execute function
			process_dbf("dummy.dbf", doctype="partner", encoding="cp1250")

			self.dbf_table_mock.open.assert_called_once()
			mock_insert.assert_any_call({"id": 1, "name": "Alice", "doctype": "partner"})
			mock_insert.assert_any_call({"id": 2, "name": "Bob", "doctype": "partner"})
			mock_remove.assert_not_called()

	def test_process_dbf_removes_records(self):
		"""Test call remove_from_db, if doctype == 'torolt'."""
		with (
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.dbf.Table", return_value=self.dbf_table_mock),
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.insert_into_db") as mock_insert,
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.remove_from_db") as mock_remove,
			patch("frappe.logger"),
		):
			process_dbf("dummy.dbf", doctype="torolt", encoding="utf-8")

			mock_remove.assert_any_call({"id": 1, "name": "Alice", "doctype": "torolt"})
			mock_remove.assert_any_call({"id": 2, "name": "Bob", "doctype": "torolt"})
			mock_insert.assert_not_called()

	def test_process_dbf_handles_dbferror(self):
		"""Test if exception in opening Dbase file, logs error"""
		import dbf

		with (
			patch(
				"vir_conto.vir_conto.doctype.data_packet.data_packet.dbf.Table",
				side_effect=dbf.exceptions.DbfError("Dbf Error"),
			),
			patch("frappe.logger") as mock_logger,
		):
			process_dbf("broken.dbf", "partner", "utf-8")
			mock_logger.return_value.exception.assert_called()

	def test_process_dbf_handles_any_error(self):
		"""Test if exception in opening Dbase file, logs error"""
		with (
			patch("vir_conto.vir_conto.doctype.data_packet.data_packet.dbf.Table", side_effect=Exception("Error")),
			patch("frappe.logger") as mock_logger,
		):
			process_dbf("broken.dbf", "partner", "utf-8")
			mock_logger.return_value.exception.assert_called()

	def test_integration_import_data_packet(self):
		# Create mock Data Packet
		file_name = "TEST-0001.LZH"
		create_datapacket(file_name)
		data_packet: DataPacket = frappe.get_doc("Data Packet", file_name)

		# Copy mock file
		copy_datapacket(data_packet, file_name)

		# Clear DB
		frappe.db.delete("raktnev")
		frappe.db.delete("tcsop")
		frappe.db.delete("tfocsop")
		frappe.db.delete("torzs")
		frappe.db.delete("vir_bolt")
		frappe.db.delete("vir_csop")

		# Execute function
		data_packet.import_packet()

		# Cleanup Data Packets
		shutil.rmtree(data_packet.get_extraction_dir())
		os.remove(data_packet.get_file_path())

		# According to TEST-0001 has:
		# Table		Num of Records
		# raktnev	5
		# tcsop		21
		# tfocsop	6
		# torzs		1
		# vir_bolt	174
		# vir_csop	927
		self.assertEqual(5, frappe.db.count("raktnev"))
		self.assertEqual(21, frappe.db.count("tcsop"))
		self.assertEqual(6, frappe.db.count("tfocsop"))
		self.assertEqual(1, frappe.db.count("torzs"))
		self.assertEqual(174, frappe.db.count("vir_bolt"))
		self.assertEqual(927, frappe.db.count("vir_csop"))

	def test_import_data_creates_extraction_dir(self):
		mock_zip = MagicMock()

		# Create mock Data Packet
		file_name = "TEST-0001.LZH"
		create_datapacket(file_name)
		data_packet: DataPacket = frappe.get_doc("Data Packet", file_name)

		with (
			patch("os.path.exists", return_value=False),
			patch("os.makedirs") as mock_makedirs,
			patch("zipfile.ZipFile", return_value=mock_zip),
			patch("frappe.db.get_list", return_value=[]),
		):
			# Execute function
			data_packet.import_packet()
			mock_makedirs.assert_called_once_with(data_packet.get_extraction_dir())

	def test_import_queues_datapackets_correctly(self):
		mock_packets = ["TEST-0001.LZH", "TEST-0002.LZH"]

		with (
			patch("frappe.utils.nowtime", return_value="12:30:00"),
			patch("frappe.logger"),
			patch("frappe.enqueue_doc") as mock_enqueue,
			patch("frappe.db.get_list", return_value=mock_packets),
		):
			# Execute function
			result = import_new_packets()

			self.assertEqual(result, 2)
			mock_enqueue.assert_any_call("Data Packet", name="TEST-0001.LZH", method="import_packet")
			mock_enqueue.assert_any_call("Data Packet", name="TEST-0002.LZH", method="import_packet")

	def test_import_returns_zero_when_no_packets(self):
		""""""
		with (
			patch("frappe.utils.nowtime", return_value="12:30:00"),
			patch("frappe.logger") as mock_logger,
			patch("frappe.enqueue_doc") as mock_enqueue,
			patch("frappe.db.get_list", return_value=[]),
		):
			# Execute function
			result = import_new_packets()

		self.assertEqual(result, 0)
		mock_enqueue.assert_not_called()
		mock_logger.return_value.info.assert_not_called()

	def test_import_logs_error_if_enqueue_fails(self):
		"""Ha enqueue_doc exception-t dob, logger.error hívódik."""
		mock_logger = MagicMock()
		mock_packets = ["TEST-0001.LZH", "TEST-0002.LZH"]

		with (
			patch("frappe.logger", return_value=mock_logger),
			patch("frappe.utils.nowtime", return_value="12:30:00"),
			patch("frappe.get_list", return_value=mock_packets),
			patch("frappe.enqueue_doc", side_effect=Exception("Error")),
		):
			# Execute function
			import_new_packets()
			mock_logger.error.assert_called_once()
			mock_logger.info.assert_any_call("Beginning to import new packets")

	def test_integration_clear_old_packets(self):
		# Create mock DataPacket
		file_name = "TEST-0001.ZIP"
		create_datapacket(file_name)
		doc: DataPacket = frappe.get_doc("Data Packet", file_name)
		frappe.db.set_value("Data Packet", file_name, "creation", frappe.utils.nowdate(), update_modified=False)
		frappe.db.commit()  # nosemgrep

		file_url = doc.get_file_path()

		copy_datapacket(doc, file_name)
		# Track uploaded archive packet
		file = Path(file_url)

		clear_old_packets()

		# SHOULD exist because its date is fresh
		self.assertIsNotNone(frappe.db.exists("Data Packet", file_name))
		self.assertTrue(file.exists())

		# Change creation date
		frappe.db.set_value("Data Packet", file_name, "creation", "2025.03.25", update_modified=False)
		frappe.db.commit()  # nosemgrep

		clear_old_packets()

		# SHOULD NOT exist because date is older than a month
		self.assertIsNone(frappe.db.exists("Data Packet", file_name))
		self.assertFalse(file.exists())
		frappe.db.commit()  # nosemgrep

	def test_clear_old_packets_logs_error_when_exception_occurs(self):
		mock_logger = MagicMock()

		with (
			patch("frappe.logger", return_value=mock_logger),
			patch("frappe.db.get_list", side_effect=Exception("DB Error")),
		):
			# Execute functions
			clear_old_packets()

			mock_logger.exception.assert_called_once()

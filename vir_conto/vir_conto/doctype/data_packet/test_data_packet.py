# Copyright (c) 2025, Alex Nagy and Contributors
# See license.txt

import os.path
import shutil
import unittest
from pathlib import Path

import frappe
import frappe.utils

from vir_conto.vir_conto.doctype.data_packet.data_packet import (
	DataPacket,
	clear_old_packets,
	get_name,
	import_new_packets,
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
		print(error)
		return False

	return True


class TestDataPacket(unittest.TestCase):
	def test_datapacket_return_correct_paths(self):
		# Create mock Data Packet
		file_name = "TEST-0001"
		create_datapacket(file_name)

		doc: DataPacket = frappe.get_doc("Data Packet", file_name)

		self.assertEqual(doc.get_file_url(), f"{frappe.get_site_path()}/private/files/{file_name}")
		self.assertEqual(doc.get_extraction_dir(), f"{frappe.get_site_path()}/private/files/storage/{file_name}")

	def test_get_name_return_correctly(self):
		test_row = {
			"kod": "901",
			"nev": "GÖNGYÖLEG",
			"rend": 0,
			"tarhely": "",
			"focsop": "200",
			"doctype": "tcsop",
		}
		self.assertEqual("901", get_name(test_row))

		# Check with composite key as well
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

		# Call import_data manually
		data_packet.import_data()

		# Cleanup Data Packets
		shutil.rmtree(data_packet.get_extraction_dir())
		os.remove(data_packet.get_file_url())

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

	def test_import_new_packets_queues_packets_correctly(self):
		# Clear Data Packet table, so the function returns if there are no packets
		frappe.db.delete("Data Packet")
		self.assertEqual(0, import_new_packets())

		# Create mock Data Packets
		file_names = ["TEST-0001.LZH", "TEST-0002.LZH"]
		data_packets = []
		for file_name in file_names:
			create_datapacket(file_name)
			data_packet: DataPacket = frappe.get_doc("Data Packet", file_name)
			data_packet.processed = False
			data_packet.save()

			copy_datapacket(data_packet, file_name)
			data_packets.append(data_packet)

		# Call import_data manually
		self.assertEqual(import_new_packets(), len(data_packets))

		# Cleanup Data Packets
		for data_packet in data_packets:
			print("Removing dir: ", data_packet.get_extraction_dir())
			shutil.rmtree(data_packet.get_extraction_dir())
			print("Removing file: ", data_packet.get_file_url())
			os.remove(data_packet.get_file_url())

	def test_clear_old_packets(self):
		frappe.set_user("Administrator")

		# Create mock DataPacket
		file_name = "TEST-0001"
		create_datapacket(file_name)

		doc: DataPacket = frappe.get_doc("Data Packet", file_name)
		frappe.db.set_value("Data Packet", file_name, "creation", frappe.utils.nowdate(), update_modified=False)
		frappe.db.commit()  # nosemgrep
		extraction_dir = doc.get_extraction_dir()
		file_url = doc.get_file_url()

		# Copy mock file
		src_path = "../apps/vir_conto/vir_conto/vir_conto/doctype/data_packet/TEST-0001"

		shutil.copy(src_path + ".LZH", file_url)
		if not os.path.exists(extraction_dir):
			os.makedirs(extraction_dir)
		# Track uploaded archive packet
		file = Path(file_url)

		clear_old_packets()

		# Here Data Packet SHOULD exist because its date is fresh
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

import dbf
import frappe
from frappe.model.document import Document

from vir_conto.vir_conto.doctype.primary_key.primary_key import PrimaryKey


def process_dbf(dbf_file: str, doctype: str, encoding: str) -> None:
	"""Holds the logic for accessing a debase table.

	Args:
	        dbf_file (str): Source path of debase file.
	        doctype (str): What doctype it needs to create.
	        encoding (str): Debase file encoded in.
	"""
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
	# frappe.db.get_all("Primary Key", filters={'type': ['=', 'TERM']})
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
	"""Creates the name aka. primary key for a Frappe document.

	Args:
	        row (dict):

	Returns:
	        str: _description_
	"""
	# Selects the primary key for the appropriate doctype
	pkey: PrimaryKey = frappe.get_doc("Primary Key", row["doctype"]).conto_primary_key
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
	"""Inserts a key:value pair row into Frappe DB

	Args:
	        row (dict): Needs 'doctype' field in order to create new document by Frapee
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


def get_frappe_version() -> str:
	"""Returns Frappe version from environment variable

	Returns:
		str: Frappe version number in string
	"""
	import os

	from dotenv import load_dotenv

	path = os.path.join(os.getcwd(), ".env")
	load_dotenv(dotenv_path=path)

	return os.environ.get("FRAPPE_VERSION")

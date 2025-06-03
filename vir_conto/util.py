import dbf
import frappe
from frappe.model.document import Document

from vir_conto.vir_conto.doctype.primary_key.primary_key import PrimaryKey


def process_dbf(dbf_file: str, doctype: str, encoding: str) -> None:
	"""Method for processing a Dbase file.

	:param dbf_file: Source path of debase file.
	:param doctype: What doctype it needs to create.
	:param encoding: Debase file encoded in.
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
	pkey_info = frappe.get_list("Primary Key", fields=["*"], filters={"type": row["tipus"]})
	row["doctype"] = pkey_info["frappe_name"]

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

	:param row: Data row must contain a 'doctype' field in order to create the key.

	:return str: Returns the correct primary key.
	"""
	# Selects the primary key for the appropriate doctype
	pkey: PrimaryKey = frappe.get_doc("Primary Key", row["doctype"]).conto_primary_key
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

	:param row: Data row must contain a 'doctype' field in order to create a new Frappe document.
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
	"""
	Returns Frappe version from environment variable.

	:return	str: Frappe version number in string.
	"""

	return frappe.hooks.app_version


from frappe.modules.import_file import delete_old_doc, import_file_by_path, read_doc_from_file
from insights.insights.doctype.insights_workbook.insights_workbook import InsightsWorkbook


def sync_default_charts():
	"""Method for synchronizing default charts with the ones in the database.

	Steps:
	        1. Import old workbooks from JSON (insights_workbook.json).
	        2. Insert any missing workbooks into the database.
	        3. Retrieve all new workbooks from the database whose title starts with '_'.
	        4. Create a lookup table to map old workbook names to new workbook IDs and titles.
	        5. For each of the following doctypes: insights_query_v3, insights_chart_v3, insights_dashboard_v3:
	         - Import documents from their respective JSON files.
	         - Update the workbook reference in each document to the new workbook ID.
	         - If the document already exists, delete and re-insert it; otherwise, insert it.
	        6. Commit the changes to the database.

	Notes:
	- This function expects the presence of JSON files for workbooks, queries, charts, and dashboards
	  in the 'charts' directory of the 'vir_conto' app.
	- The function assumes that workbook titles are unique identifiers for mapping.
	- If a required JSON file is missing, the function will print a message and return early.
	"""
	path = frappe.get_app_path("vir_conto", "charts", "insights_workbook.json")
	# 1. (OLD) Import old title and name of workbook from JSON
	try:
		docs = read_doc_from_file(path)
	except OSError:
		print(f"{path} missing")
		return

	if docs:
		if not isinstance(docs, list):
			docs = [docs]
		import_workbooks: list[InsightsWorkbook] = [frappe.get_doc(doc) for doc in docs]

	# 2. Check if a default workbook exists
	for import_workbook in import_workbooks:
		if not frappe.db.exists("Insights Workbook", {"title": import_workbook.title}):
			# If not creates a new
			import_workbook.insert()

	# 3. (NEW) Get all workbooks title and name
	new_workbooks: list[InsightsWorkbook] = frappe.get_all(
		"Insights Workbook", fields=["*"], filters=[["title", "like", "_%"]]
	)

	# 4. Create lookup table for migrating queries, charts, dashboards
	workbook_dict = {}
	for new_workbook in new_workbooks:
		new_title = new_workbook.title
		new_id = new_workbook.name
		match_name = next(
			import_workbook.name for import_workbook in import_workbooks if import_workbook.title == new_title
		)

		workbook_dict[match_name] = {"new_id": new_id, "new_title": new_title}

	# 5. Import the rest (queries, charts, dashboards)
	doctypes = ["insights_query_v3", "insights_chart_v3", "insights_dashboard_v3"]
	for doctype in doctypes:
		path = frappe.get_app_path("vir_conto", "charts", doctype + ".json")
		try:
			docs = read_doc_from_file(path)
		except OSError:
			print(f"{path} missing")
			return

		if docs:
			if not isinstance(docs, list):
				docs = [docs]
			for doc in docs:
				import_doc = frappe.get_doc(doc)

				# 6. update workbook name accordingly
				old_id = import_doc.workbook

				new_id = workbook_dict.get(int(old_id))["new_id"]
				import_doc.workbook = new_id

				if frappe.db.exists(import_doc.doctype, import_doc.name):
					old_name = import_doc.name
					delete_old_doc(import_doc, reset_permissions=False)
					import_doc.insert(ignore_links=True, set_name=old_name)
				else:
					import_doc.insert(ignore_links=True)
			frappe.db.commit()  # nosemgrep

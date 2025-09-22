import os

import frappe
from dotenv import load_dotenv


def after_uninstall():
	path = os.path.join(os.getcwd(), ".env")
	load_dotenv(dotenv_path=path)
	remove_system_user()
	remove_insights_teams()

	frappe.db.commit()


def remove_system_user():
	print("Removing System User", os.environ.get("CONTO_SYS_USR_USERNAME"))
	frappe.delete_doc("User", os.environ.get("CONTO_SYS_USR_USERNAME"))


def remove_insights_teams():
	print("Removing Custom Insights Team", "'Tulajdonos'")
	frappe.delete_doc("Insights Team", "Tulajdonos")

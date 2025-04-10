import os

import frappe
from dotenv import load_dotenv
from frappe.utils.password import update_password


def after_install():
	# path = os.path.join(os.getcwd(), frappe.get_site_path()[2:], ".env")
	# TODO:
	# - set system settings to hungarian
	pass


def after_sync():
	path = os.path.join(os.getcwd(), ".env")
	load_dotenv(dotenv_path=path)
	# create_system_user_profiles()
	create_system_user()


# def create_system_user_profiles():
# if not frappe.db.exists("Role Profile", "cconto_system_user_profile"):


def create_system_user():
	new_user = frappe.new_doc("User")

	new_user.email = os.environ.get("CCONTO_SYS_USR_EMAIL")
	new_user.username = os.environ.get("CCONTO_SYS_USR_USERNAME")
	new_user.first_name = os.environ.get("CCONTO_SYS_USR_USERNAME")
	new_user.language = "en"
	new_user.time_zone = "Europe/Budapest"
	new_user.append("role_profiles", {"role_profile": "cconto_system_user_profile"})
	new_user.module_profile = "cconto_system_user_profile"

	new_user.insert()
	update_password(new_user.name, os.environ.get("CCONTO_SYS_USR_PASSWORD"))

	# TODO:
	#  - Generate API key to access from main program.

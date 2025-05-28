import json
import os

import frappe
from dotenv import load_dotenv
from frappe.core.doctype.user.user import User
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
from frappe.utils.password import update_password

from vir_conto.util import get_frappe_version


def load_environment():
	path = os.path.join(os.getcwd(), ".env")
	if not load_dotenv(dotenv_path=path):
		raise FileNotFoundError(
			"Vir Conto environment file not found, make sure to place it in bench/sites folder!"
		)


def after_install() -> None:
	# TODO:
	# - set system settings to hungarian
	# pass
	load_environment()
	run_setup_wizard()


def after_sync() -> None:
	load_environment()
	create_system_user()


def create_system_user() -> None:
	print("Creating System User")

	email = os.environ.get("CONTO_SYS_USR_EMAIL")
	username = os.environ.get("CONTO_SYS_USR_USERNAME")
	password = os.environ.get("CONTO_SYS_USR_PASSWORD")

	if not (email and username and password):
		raise Exception("Missing required environment variables for system user.")

		# Check if the user already exists
	if frappe.db.exists("User", {"email": email}):
		print(f"User with email {email} already exists.")
		return

	new_user: User = frappe.new_doc("User")

	print("Configuring System User")
	new_user.email = email
	new_user.username = username
	new_user.first_name = username
	new_user.language = "en"
	new_user.time_zone = "Europe/Budapest"

	# Working with devel but not with ver.: 15
	if int(get_frappe_version().split(".")[0]) <= 15:
		new_user.role_profile_name = "conto_system_role_profile"
		new_user.module_profile = "conto_system_module_profile"
	else:
		new_user.append("role_profiles", {"role_profile": "conto_system_role_profile"})
		new_user.module_profile = "conto_system_module_profile"

	new_user.insert(set_name=email)
	update_password(new_user.name, password)

	print("Generating API key")
	api_key = frappe.generate_hash(length=15)
	api_secret = frappe.generate_hash(length=15)
	new_user.api_key = api_key
	new_user.api_secret = api_secret
	new_user.save()

	# Write API key to key.json
	key_path = os.path.join(frappe.get_site_path(), "key.json")
	with open(key_path, "w", encoding="utf8") as json_file:
		json.dump({"api_key": api_key, "api_secret": api_secret}, json_file, ensure_ascii=True)


def run_setup_wizard():
	if frappe.db.get_single_value("System Settings", "setup_complete"):
		print("Setup already completed.")
		return

	args = {
		"language": "English",
		"country": "Hungary",
		"currency": "HUF",
		"timezone": "Europe/Budapest",
		# "full_name": "Administrator",
		# "email": "admin@example.com",
		# "password": os.environ.get("ADMIN_PASSWORD"),
		"setup_demo": 0,
		"disable_telemetry": 0,
	}

	# CI set to true otherwise Insights will install demo data
	os.environ["CI"] = "1"

	setup_status = setup_complete(args=args)

	if setup_status.get("status") != "ok":
		frappe.throw("Frappe setup failed")

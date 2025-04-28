import json
import os

import frappe
from dotenv import load_dotenv
from frappe.core.doctype.user.user import User
from frappe.utils.password import update_password

from vir_conto.util import get_frappe_version


def after_install():
	# TODO:
	# - set system settings to hungarian
	pass


def after_sync():
	path = os.path.join(os.getcwd(), ".env")
	load_dotenv(dotenv_path=path)

	create_system_user()


def create_system_user() -> None:
	print("Creating System User")
	new_user: User = frappe.new_doc("User")

	print("Configuring System User")
	new_user.email = os.environ.get("CONTO_SYS_USR_EMAIL")
	new_user.username = os.environ.get("CONTO_SYS_USR_USERNAME")
	new_user.first_name = os.environ.get("CONTO_SYS_USR_USERNAME")
	new_user.language = "en"
	new_user.time_zone = "Europe/Budapest"

	# Working with devel but not with ver.: 15
	if int(get_frappe_version().split(".")[0]) <= 15:
		new_user.role_profile_name = "conto_system_user_profile"
		new_user.module_profile = "conto_system_user_profile"
	else:
		new_user.append("role_profiles", {"role_profile": "conto_system_user_profile"})
		new_user.module_profile = "conto_system_user_profile"

	new_user.insert()
	update_password(new_user.name, os.environ.get("CONTO_SYS_USR_PASSWORD"))

	print("Generating API key")
	api_key = frappe.generate_hash(length=15)
	api_secret = frappe.generate_hash(length=15)
	new_user.api_key = api_key
	new_user.api_secret = api_secret
	new_user.save()
	key_path = os.path.join(frappe.get_site_path(), "key.json")
	with open(key_path, "w", encoding="utf8") as json_file:
		json.dump({"api_key": api_key, "api_secret": api_secret}, json_file, ensure_ascii=True)

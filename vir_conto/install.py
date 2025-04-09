import os

import frappe
from frappe.utils.password import update_password


def after_install():
	# create_system_user_profiles()
	create_system_user()


def create_system_user():
	new_user = frappe.new_doc("User")
	new_user.email = os.environ.get("CCONTO_SYSTEM_USR_EMAIL")
	new_user.username = os.environ.get("CCONTO_SYSTEM_USR_USERNAME")
	new_user.first_name = os.environ.get("CCONTO_SYSTEM_USR_USERNAME")
	# new_user.append("role_profiles", {"role_profile": "cconto_system_user_profile"})
	# new_user.module_profile = "cconto_system_user_profile"

	new_user.insert()
	update_password(new_user.name, os.environ.get("CCONTO_SYSTEM_USR_PASSWORD"))

	# TODO:
	#  - Generate API key to access from main program.

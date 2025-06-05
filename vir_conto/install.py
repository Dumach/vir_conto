import json
import os

import frappe
from dotenv import load_dotenv
from frappe import _
from frappe.core.doctype.user.user import User
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
from frappe.utils.password import update_password

from vir_conto.util import get_frappe_version, sync_default_charts


def load_environment():
	"""Method for loading environment file from bench/sites folder.

	Raises:
	        FileNotFoundError: if the file is not found, therefore the installation should not continue in this way.
	"""
	path = os.path.join(os.getcwd(), ".env")
	if not load_dotenv(dotenv_path=path):
		raise FileNotFoundError(
			"Vir Conto environment file not found, make sure to place it in bench/sites folder!"
		)


# will run after app is installed on site
def after_install() -> None:
	# TODO:
	# - set system settings to hungarian

	load_environment()
	run_setup_wizard()


# will run after app fixtures are synced
def after_sync() -> None:
	load_environment()
	create_system_user()

	# Import default charts manually instead of relying on fixtures to handle
	import_charts()
	sync_default_charts()

	create_insights_teams()


def create_system_user() -> None:
	"""Method for creating a system user that will handle the synchronization of Data Packet from Conto.

	Raises:
	        Exception: If email or username or password is missing.
	"""
	print("Creating System User")

	email = os.environ.get("CONTO_SYS_USR_EMAIL")
	username = os.environ.get("CONTO_SYS_USR_USERNAME")
	password = os.environ.get("CONTO_SYS_USR_PASSWORD")

	if not (email and username and password):
		raise Exception("Missing required environment variables for system user.")

	# Check if user already exists
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

	# Version 16 handles Role Profiles differently
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
	"""Method for completing the setup wizard."""
	if frappe.db.get_single_value("System Settings", "setup_complete"):
		print("Setup already completed.")
		return

	args = {
		"language": "English",
		"country": "Hungary",
		"currency": "HUF",
		"float_precision": 4,
		"first_day_of_the_week": "Monday",
		"timezone": "Europe/Budapest",
		# "full_name": "Administrator",
		# "email": "admin@example.com",
		# "password": os.environ.get("ADMIN_PASSWORD"),
		"session_expiry": "24:00",
		"setup_demo": 0,
		"disable_telemetry": 0,
	}

	# CI set to true otherwise Insights will install demo data
	os.environ["CI"] = "1"

	setup_status = setup_complete(args=args)

	if setup_status.get("status") != "ok":
		frappe.throw(frappe._("Frappe setup failed"))


def import_charts() -> None:
	"""Method for importing Insights charts from 'bench/apps/myapp/charts' folder."""
	from frappe.utils.fixtures import import_doc

	# Code from frappe.utils.fixtures.import_fixtures
	fixtures_path = frappe.get_app_path("vir_conto", "charts")
	if not os.path.exists(fixtures_path):
		return

	fixture_files = os.listdir(fixtures_path)

	for fname in fixture_files:
		if not fname.endswith(".json"):
			continue

		file_path = frappe.get_app_path("vir_conto", "charts", fname)
		try:
			import_doc(file_path)
		except (ImportError, frappe.DoesNotExistError) as e:
			# fixture syncing for missing doctypes
			print(f"Skipping fixture syncing from the file {fname}. Reason: {e}")


def create_insights_teams():
	try:
		team_tulaj = frappe.new_doc("Insights Team")
		team_tulaj.team_name = "Tulajdonos"
		team_tulaj.append("team_members", {"user": "Administrator"})

		team_tulaj.insert()
	except ImportError as error:
		print(error)

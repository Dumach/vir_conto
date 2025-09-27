import json
import os
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

import frappe
from frappe.core.doctype.user.user import User


class TestInstallModule(unittest.TestCase):
	"""Test suite for install.py module functions."""

	@classmethod
	def setUpClass(cls):
		"""Set up test class with required test records."""
		frappe.set_user("Administrator")

	def setUp(self):
		"""Set up test data before each test."""
		# Mock environment variables
		self.env_vars = {
			"CONTO_SYS_USR_EMAIL": "test@example.com",
			"CONTO_SYS_USR_USERNAME": "test_user",
			"CONTO_SYS_USR_PASSWORD": "test_password",
			"ADMIN_PASSWORD": "admin_password",
		}

	def tearDown(self):
		"""Clean up after each test."""
		frappe.db.rollback()

	def test_load_environment_success(self):
		"""Test successful environment file loading."""
		from vir_conto.install import load_environment

		with (
			patch("vir_conto.install.os.path.join") as mock_path_join,
			patch("vir_conto.install.load_dotenv") as mock_load_dotenv,
		):
			mock_path_join.return_value = "/test/path/.env"
			mock_load_dotenv.return_value = True

			# Should not raise any exception
			load_environment()

			mock_path_join.assert_called_once_with(os.getcwd(), ".env")
			mock_load_dotenv.assert_called_once_with(dotenv_path="/test/path/.env")

	def test_load_environment_file_not_found(self):
		"""Test environment file loading when file is not found."""
		from vir_conto.install import load_environment

		with (
			patch("vir_conto.install.os.path.join") as mock_path_join,
			patch("vir_conto.install.load_dotenv") as mock_load_dotenv,
		):
			mock_path_join.return_value = "/test/path/.env"
			mock_load_dotenv.return_value = False

			with self.assertRaises(FileNotFoundError) as context:
				load_environment()

			self.assertIn("Vir Conto environment file not found", str(context.exception))

	def test_after_install(self):
		"""Test after_install function execution."""
		from vir_conto.install import after_install

		with (
			patch("vir_conto.install.create_insights_teams"),
			patch("vir_conto.install.sync_default_charts"),
			patch("vir_conto.install.create_system_user"),
			patch("vir_conto.install.add_workbook_custom_fields") as mock_add_fields,
			patch("vir_conto.install.run_setup_wizard") as mock_setup_wizard,
			patch("vir_conto.install.load_environment") as mock_load_env,
		):
			after_install()

			mock_load_env.assert_called_once()
			mock_setup_wizard.assert_called_once()
			mock_add_fields.execute.assert_called_once()

	def test_after_sync(self):
		"""Test after_sync function execution."""
		from datetime import date

		from vir_conto.install import after_sync

		with (
			patch("vir_conto.install.create_insights_teams") as mock_create_teams,
			patch("vir_conto.install.sync_default_charts") as mock_sync_charts,
			patch("vir_conto.install.create_system_user") as mock_create_user,
			patch("vir_conto.install.load_environment") as mock_load_env,
			patch("frappe.db.set_single_value") as mock_set_single,
			patch("frappe.utils.getdate") as mock_getdate,
		):
			mock_date = date(2024, 5, 15)
			mock_getdate.return_value = mock_date

			after_sync()

			mock_load_env.assert_called_once()
			mock_create_user.assert_called_once()
			mock_sync_charts.assert_called_once()
			mock_create_teams.assert_called_once()

			# Check Insights Settings configuration
			mock_set_single.assert_any_call("Insights Settings", "fiscal_year_start", "2024-01-01")
			mock_set_single.assert_any_call("Insights Settings", "week_starts_on", "Monday")

	def test_create_system_user_missing_env_vars(self):
		"""Test create_system_user with missing environment variables."""
		from vir_conto.install import create_system_user

		with patch.dict("os.environ", {}, clear=True):
			with self.assertRaises(Exception) as context:
				create_system_user()

			self.assertIn("Missing required environment variables", str(context.exception))

	def test_create_system_user_partial_env_vars(self):
		"""Test create_system_user with partially missing environment variables."""
		from vir_conto.install import create_system_user

		test_env = {
			"CONTO_SYS_USR_EMAIL": "test@example.com",
			"CONTO_SYS_USR_USERNAME": "",
			"CONTO_SYS_USR_PASSWORD": "password",
		}

		with patch.dict("os.environ", test_env, clear=True):
			with self.assertRaises(Exception) as context:
				create_system_user()

			self.assertIn("Missing required environment variables", str(context.exception))

	def test_create_system_user_already_exists(self):
		"""Test create_system_user when user already exists."""
		from vir_conto.install import create_system_user

		test_env = {
			"CONTO_SYS_USR_EMAIL": "existing@example.com",
			"CONTO_SYS_USR_USERNAME": "existing_user",
			"CONTO_SYS_USR_PASSWORD": "password",
		}

		with patch.dict("os.environ", test_env, clear=True), patch("frappe.db.exists") as mock_exists:
			mock_exists.return_value = True

			# Should complete without creating new user
			create_system_user()

			mock_exists.assert_called_once_with("User", {"email": "existing@example.com"})

	def test_create_system_user_success_v15(self):
		"""Test successful system user creation for Frappe v15."""
		from vir_conto.install import create_system_user

		test_env = {
			"CONTO_SYS_USR_EMAIL": "new@example.com",
			"CONTO_SYS_USR_USERNAME": "new_user",
			"CONTO_SYS_USR_PASSWORD": "password",
		}

		with (
			patch.dict("os.environ", test_env, clear=True),
			patch("frappe.db.exists") as mock_exists,
			patch("frappe.new_doc") as mock_new_doc,
			patch("vir_conto.install.update_password") as mock_update_password,
			patch("frappe.generate_hash") as mock_generate_hash,
			patch("frappe.get_site_path") as mock_get_site_path,
			patch("frappe.hooks.app_version", "15.0.0"),
		):
			mock_exists.return_value = False
			mock_user = Mock(spec=User)
			mock_user.name = "new@example.com"  # Add name attribute for update_password call
			mock_new_doc.return_value = mock_user
			mock_generate_hash.side_effect = ["api_key_123", "api_secret_456"]
			mock_get_site_path.return_value = "/test/site/path"

			with patch("builtins.open", mock_open()) as mock_file:
				create_system_user()

			# Verify user creation
			mock_new_doc.assert_called_once_with("User")
			self.assertEqual(mock_user.email, "new@example.com")
			self.assertEqual(mock_user.username, "new_user")
			self.assertEqual(mock_user.first_name, "new_user")
			self.assertEqual(mock_user.language, "en")
			self.assertEqual(mock_user.time_zone, "Europe/Budapest")
			self.assertEqual(mock_user.role_profile_name, "conto_system_role_profile")
			self.assertEqual(mock_user.module_profile, "conto_system_module_profile")

			# Verify API key generation and file writing
			mock_user.insert.assert_called_once_with(set_name="new@example.com")
			mock_update_password.assert_called_once_with(mock_user.name, "password")
			self.assertEqual(mock_user.api_key, "api_key_123")
			self.assertEqual(mock_user.api_secret, "api_secret_456")
			mock_user.save.assert_called_once()

			# Verify key.json file creation
			mock_file.assert_called_once_with("/test/site/path/key.json", "w", encoding="utf8")

	def test_create_system_user_success_v16(self):
		"""Test successful system user creation for Frappe v16+."""
		from vir_conto.install import create_system_user

		test_env = {
			"CONTO_SYS_USR_EMAIL": "new@example.com",
			"CONTO_SYS_USR_USERNAME": "new_user",
			"CONTO_SYS_USR_PASSWORD": "password",
		}

		with (
			patch.dict("os.environ", test_env, clear=True),
			patch("frappe.db.exists") as mock_exists,
			patch("frappe.new_doc") as mock_new_doc,
			patch("vir_conto.install.update_password") as _mock_update_password,
			patch("frappe.generate_hash") as mock_generate_hash,
			patch("frappe.get_site_path") as mock_get_site_path,
			patch("frappe.hooks.app_version", "16.0.0"),
		):
			mock_exists.return_value = False
			mock_user = Mock(spec=User)
			mock_user.name = "new@example.com"  # Add name attribute for update_password call
			mock_user.append = Mock()
			mock_new_doc.return_value = mock_user
			mock_generate_hash.side_effect = ["api_key_123", "api_secret_456"]
			mock_get_site_path.return_value = "/test/site/path"

			with patch("builtins.open", mock_open()) as _mock_file:
				create_system_user()

			# Verify v16+ role profile handling
			mock_user.append.assert_called_once_with("role_profiles", {"role_profile": "conto_system_role_profile"})
			self.assertEqual(mock_user.module_profile, "conto_system_module_profile")

	def test_run_setup_wizard_already_completed(self):
		"""Test run_setup_wizard when setup is already completed."""
		from vir_conto.install import run_setup_wizard

		with patch("frappe.db.get_single_value") as mock_get_single_value:
			mock_get_single_value.return_value = True

			# Should return early without calling setup_complete
			run_setup_wizard()

			mock_get_single_value.assert_called_once_with("System Settings", "setup_complete")

	@patch.dict("os.environ", {}, clear=True)
	def test_run_setup_wizard_success(self):
		"""Test successful setup wizard execution."""
		from vir_conto.install import run_setup_wizard

		with (
			patch("frappe.db.get_single_value") as mock_get_single_value,
			patch("vir_conto.install.setup_complete") as mock_setup_complete,
		):
			mock_get_single_value.return_value = False
			mock_setup_complete.return_value = {"status": "ok"}

			run_setup_wizard()

			# Verify CI environment variable is set
			self.assertEqual(os.environ.get("CI"), "1")

			# Verify setup_complete is called with correct arguments
			expected_args = {
				"language": "English",
				"country": "Hungary",
				"currency": "HUF",
				"float_precision": 4,
				"first_day_of_the_week": "Monday",
				"timezone": "Europe/Budapest",
				"session_expiry": "24:00",
				"setup_demo": 0,
				"disable_telemetry": 0,
			}
			mock_setup_complete.assert_called_once_with(args=expected_args)

	def test_run_setup_wizard_failure(self):
		"""Test setup wizard execution failure."""
		from vir_conto.install import run_setup_wizard

		with (
			patch("frappe.db.get_single_value") as mock_get_single_value,
			patch("vir_conto.install.setup_complete") as mock_setup_complete,
			patch("frappe.throw") as mock_throw,
		):
			mock_get_single_value.return_value = False
			mock_setup_complete.return_value = {"status": "error"}

			run_setup_wizard()

			mock_throw.assert_called_once()

	def test_create_insights_teams_success(self):
		"""Test successful creation of insights teams."""
		from vir_conto.install import create_insights_teams

		with patch("frappe.new_doc") as mock_new_doc:
			mock_team = Mock()
			mock_team.append = Mock()
			mock_team.insert = Mock()
			mock_new_doc.return_value = mock_team

			create_insights_teams()

			mock_new_doc.assert_called_once_with("Insights Team")
			self.assertEqual(mock_team.team_name, "Tulajdonos")
			mock_team.append.assert_called_once_with("team_members", {"user": "Administrator"})
			mock_team.insert.assert_called_once()

	def test_create_insights_teams_import_error(self):
		"""Test create_insights_teams handling ImportError."""
		from vir_conto.install import create_insights_teams

		with patch("frappe.new_doc") as mock_new_doc:
			mock_new_doc.side_effect = ImportError("Test import error")

			# Should not raise exception, just print error
			create_insights_teams()

			mock_new_doc.assert_called_once_with("Insights Team")


class TestUninstallModule(unittest.TestCase):
	"""Test suite for uninstall.py module functions."""

	@classmethod
	def setUpClass(cls):
		"""Set up test class with required test records."""
		frappe.set_user("Administrator")

	def setUp(self):
		"""Set up test data before each test."""
		pass

	def tearDown(self):
		"""Clean up after each test."""
		frappe.db.rollback()

	def test_after_uninstall(self):
		"""Test after_uninstall function execution."""
		from vir_conto.uninstall import after_uninstall

		with (
			patch("vir_conto.uninstall.load_dotenv") as mock_load_dotenv,
			patch("vir_conto.uninstall.remove_system_user") as mock_remove_user,
			patch("vir_conto.uninstall.remove_insights_teams") as mock_remove_teams,
			patch("frappe.db.commit") as mock_commit,
		):
			mock_load_dotenv.return_value = True

			after_uninstall()

			mock_load_dotenv.assert_called_once()
			mock_remove_user.assert_called_once()
			mock_remove_teams.assert_called_once()
			mock_commit.assert_called_once()

	def test_remove_system_user_success(self):
		"""Test successful system user removal."""
		from vir_conto.uninstall import remove_system_user

		with (
			patch.dict("os.environ", {"CONTO_SYS_USR_USERNAME": "test_user"}),
			patch("frappe.delete_doc") as mock_delete_doc,
		):
			remove_system_user()

			mock_delete_doc.assert_called_once_with("User", "test_user")

	def test_remove_system_user_no_env_var(self):
		"""Test system user removal with missing environment variable."""
		from vir_conto.uninstall import remove_system_user

		with patch.dict("os.environ", {}, clear=True), patch("frappe.delete_doc") as mock_delete_doc:
			remove_system_user()

			mock_delete_doc.assert_called_once_with("User", None)

	def test_remove_insights_teams_success(self):
		"""Test successful insights teams removal."""
		from vir_conto.uninstall import remove_insights_teams

		with patch("frappe.delete_doc") as mock_delete_doc:
			remove_insights_teams()

			mock_delete_doc.assert_called_once_with("Insights Team", "Tulajdonos")

	def test_remove_system_user_delete_error(self):
		"""Test system user removal with delete error."""
		from vir_conto.uninstall import remove_system_user

		with patch("frappe.delete_doc") as mock_delete_doc:
			mock_delete_doc.side_effect = frappe.DoesNotExistError("User does not exist")

			# Should not raise exception, frappe.delete_doc handles errors internally
			with self.assertRaises(frappe.DoesNotExistError):
				remove_system_user()

	def test_remove_insights_teams_delete_error(self):
		"""Test insights teams removal with delete error."""
		from vir_conto.uninstall import remove_insights_teams

		with patch("frappe.delete_doc") as mock_delete_doc:
			mock_delete_doc.side_effect = frappe.DoesNotExistError("Team does not exist")

			# Should not raise exception, frappe.delete_doc handles errors internally
			with self.assertRaises(frappe.DoesNotExistError):
				remove_insights_teams()


class TestInstallIntegration(unittest.TestCase):
	"""Integration tests for install/uninstall workflow."""

	@classmethod
	def setUpClass(cls):
		"""Set up test class with required test records."""
		frappe.set_user("Administrator")

	def setUp(self):
		"""Set up test data before each test."""
		pass

	def tearDown(self):
		"""Clean up after each test."""
		frappe.db.rollback()

	def test_install_uninstall_workflow(self):
		"""Test complete install and uninstall workflow."""
		from datetime import date

		from vir_conto.install import after_install, after_sync
		from vir_conto.uninstall import after_uninstall

		with (
			patch("vir_conto.install.load_environment") as mock_load_env,
			patch("frappe.db.get_single_value") as mock_get_single_value,
			patch("vir_conto.install.run_setup_wizard") as _mock_run_setup,
			patch("vir_conto.install.create_system_user") as _mock_create_user,
			patch("vir_conto.install.sync_default_charts") as _mock_sync_charts,
			patch("vir_conto.install.create_insights_teams") as _mock_create_teams,
			patch("frappe.utils.getdate") as mock_getdate,
			patch("frappe.db.set_single_value") as _mock_set_single,
		):
			mock_get_single_value.return_value = True  # Setup already complete
			mock_load_env.return_value = None
			mock_getdate.return_value = date(2024, 1, 1)

			after_sync()

			# Verify core functions were called
			mock_load_env.assert_called()

		# Test uninstall workflow
		with (
			patch("vir_conto.uninstall.remove_system_user") as mock_remove_user,
			patch("vir_conto.uninstall.remove_insights_teams") as mock_remove_teams,
			patch("frappe.db.commit") as mock_commit,
			patch("vir_conto.uninstall.load_dotenv") as mock_load_dotenv,
		):
			mock_load_dotenv.return_value = True

			after_uninstall()

			mock_remove_user.assert_called_once()
			mock_remove_teams.assert_called_once()
			mock_commit.assert_called_once()

	def test_environment_variable_validation(self):
		"""Test validation of required environment variables."""
		from vir_conto.install import create_system_user

		test_cases = [
			{},  # Empty env
			{"CONTO_SYS_USR_EMAIL": "test@test.com"},  # Missing username and password
			{"CONTO_SYS_USR_USERNAME": "user"},  # Missing email and password
			{"CONTO_SYS_USR_PASSWORD": "pass"},  # Missing email and username
			{"CONTO_SYS_USR_EMAIL": "test@test.com", "CONTO_SYS_USR_USERNAME": "user"},  # Missing password
		]

		for env_vars in test_cases:
			with self.subTest(env_vars=env_vars):
				with patch.dict("os.environ", env_vars, clear=True):
					with self.assertRaises(Exception) as context:
						create_system_user()
					self.assertIn("Missing required environment variables", str(context.exception))

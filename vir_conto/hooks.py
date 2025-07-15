app_name = "vir_conto"
app_title = "Vir Conto"
app_publisher = "Alex Nagy"
app_description = "Business Intelligence for C-Conto"
app_email = "nagyalex003@gmail.com"
app_license = "agpl-3.0"

# Apps
# ------------------

required_apps = ["insights"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "vir_conto",
# 		"logo": "/assets/vir_conto/logo.png",
# 		"title": "Vir Conto",
# 		"route": "/vir_conto",
# 		"has_permission": "vir_conto.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vir_conto/css/vir_conto.css"
# app_include_js = "/assets/vir_conto/js/vir_conto.js"

# include js, css files in header of web template
# web_include_css = "/assets/vir_conto/css/vir_conto.css"
# web_include_js = "/assets/vir_conto/js/vir_conto.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vir_conto/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vir_conto/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Fixtures
# ----------
fixtures = [
	# Conto Migration
	{"dt": "Primary Key"},
	# User Permission
	{"dt": "Role", "filters": [["role_name", "like", "conto_system"]]},
	{"dt": "Role Profile", "filters": [["role_profile", "like", "conto_system_role_profile"]]},
	{"dt": "Module Profile", "filters": [["name", "like", "conto_system_module_profile"]]},
	# Queries, Charts, Dashboards
	# use export-insights in commands.py
]


# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "vir_conto.utils.jinja_methods",
# 	"filters": "vir_conto.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "vir_conto.install.before_install"
after_install = "vir_conto.install.after_install"
after_sync = "vir_conto.install.after_sync"
# Uninstallation
# ------------

# before_uninstall = "vir_conto.uninstall.before_uninstall"
after_uninstall = "vir_conto.uninstall.after_uninstall"

# Migration
# ------------
after_migrate = "vir_conto.migrate.after_migrate"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vir_conto.utils.before_app_install"
# after_app_install = "vir_conto.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vir_conto.utils.before_app_uninstall"
# after_app_uninstall = "vir_conto.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vir_conto.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		# 		"vir_conto.tasks.all"
		# "vir_conto.vir_conto.doctype.data_packet.data_packet.import_new_packets"
	],
	"daily": [
		# 		"vir_conto.tasks.daily"
		"vir_conto.vir_conto.doctype.data_packet.data_packet.clear_old_packets"
	],
	"hourly": [
		# 		"vir_conto.tasks.hourly"
		"vir_conto.vir_conto.doctype.data_packet.data_packet.import_new_packets"
	],
	# "weekly": [
	# 		"vir_conto.tasks.weekly"
	# ],
	# 	"monthly": [
	# 		"vir_conto.tasks.monthly"
	# 	],
}

# Testing
# -------

# before_tests = "vir_conto.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vir_conto.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vir_conto.task.get_dashboard_data"
# }

override_doctype_class = {"Insights Workbook": "vir_conto.overrides.insights_workbook.CustomInsightsWorkbook"}


# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vir_conto.utils.before_request"]
# after_request = ["vir_conto.utils.after_request"]

# Job Events
# ----------
# before_job = ["vir_conto.utils.before_job"]
# after_job = ["vir_conto.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"vir_conto.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

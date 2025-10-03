import frappe
from frappe import _
from insights.insights.doctype.insights_workbook.insights_workbook import InsightsWorkbook


class CustomInsightsWorkbook(InsightsWorkbook):
	def before_save(self):
		self.check_default_title_schema()
		super().before_save()

	def check_default_title_schema(self):
		"""Informs user and modifies the title if similar to the default Workbook title schema"""
		user_roles = set(frappe.get_roles(frappe.session.user))
		admin_roles = {"System Manager"}

		# Only change title if user has none of the admin roles
		if self.title.startswith("_") and user_roles.isdisjoint(admin_roles):
			self.title = self.title.lstrip("_")
			self.is_default = 0
			frappe.msgprint(
				_(
					"Workbook creation with default title schema like (_Account) is not allowed. Workbook title renamed."
				),
				indicator="yellow",
			)

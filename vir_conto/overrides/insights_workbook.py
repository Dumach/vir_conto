import frappe
from frappe import _
from insights.insights.doctype.insights_workbook.insights_workbook import InsightsWorkbook


class CustomInsightsWorkbook(InsightsWorkbook):
	def validate(self):
		if self.is_default and not self.vir_id:
			frappe.throw(
				_("The workbook is set to default but 'vir_id' is empty." + " Please set 'vir_id' or set to false.")
			)

		# Only change title if user has none of the admin roles
		if self.title is None:
			return

		user_roles = set(frappe.get_roles(frappe.session.user))
		admin_roles = {"System Manager"}
		if self.title.startswith("_") and user_roles.isdisjoint(admin_roles):
			self.title = self.title.lstrip("_")
			self.is_default = 0
			frappe.throw(
				_(
					"Workbook creation with default title schema like (_Account) is not allowed."
					+ " Workbook title renamed."
				),
			)

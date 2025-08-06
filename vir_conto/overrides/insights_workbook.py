import frappe
from frappe import _
from insights.insights.doctype.insights_workbook.insights_workbook import InsightsWorkbook


class CustomInsightsWorkbook(InsightsWorkbook):
	def before_save(self):
		self.check_default_title_schema()
		# self.generate_vir_id_if_needed()
		super().before_save()

	def check_default_title_schema(self):
		"""Informs user and modifies the title if similar to the default Workbook title schema"""
		user_roles = set(frappe.get_roles(frappe.session.user))
		admin_roles = {"conto_system", "Insights Admin"}

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

	def generate_vir_id(self):
		"""Generate `vir_id` and set `is_default` for default workbooks"""
		if not self.title.startswith("_"):
			return

		# Generate vir_id if not already set
		if not self.vir_id:
			title_clean = self.title.lstrip("_").lower().replace(" ", "_")
			self.vir_id = f"vir-{title_clean}"

		self.is_default = 1
		self.save()

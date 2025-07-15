import frappe
from frappe import _
from insights.insights.doctype.insights_workbook.insights_workbook import InsightsWorkbook


class CustomInsightsWorkbook(InsightsWorkbook):
	def before_save(self):
		self.check_default_title_schema()
		super().before_save()

	def check_default_title_schema(self):
		"""Informs user and modifies the title if similar to the default Workbook title schema"""
		if self.title.startswith("_"):
			self.title = self.title.lstrip("_")
			frappe.msgprint(
				_(
					"Workbook creation with default title schema like (_Account) is not allowed. Workbook title renamed."
				),
				indicator="yellow",
			)

import frappe


def execute():
	"""Set `ho_nap` field with data from `datum` in vir_bolt, vir_csop

	UPDATE `tabvir_bolt`
	SET ho_nap = concat(substring(datum,6,2), substring(datum,9,2));
	"""

	# vir_bolt
	frappe.db.sql(
		"""
			UPDATE `tabvir_bolt`
			SET ho_nap = concat(substring(datum,6,2), substring(datum,9,2));
		"""
	)

	# vir_csop
	frappe.db.sql(
		"""
			UPDATE `tabvir_csop`
			SET ho_nap = concat(substring(datum,6,2), substring(datum,9,2));
		"""
	)

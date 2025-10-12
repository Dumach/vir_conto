def after_migrate():
	from vir_conto.util import sync_default_charts

	print("Updating default Charts")
	sync_default_charts()

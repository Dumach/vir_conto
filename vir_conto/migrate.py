def after_migrate():
	from .util import sync_default_charts

	print("Synchronizing default Charts")
	sync_default_charts()

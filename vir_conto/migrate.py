def after_migrate():
	from .util import sync_default_charts

	sync_default_charts()

from pip._internal.utils.misc import get_installed_distributions
for _i in get_installed_distributions():
	print('project_name : {} , version : {} , Path : {}'.format(_i.project_name,_i.version,_i.location))

from pip._internal.utils.misc import get_installed_distributions
_p=get_installed_distributions()
print(_p[0].project_name)
print(_p[0].version)
print(_p[0].egg_name)
print(_p[0].location)

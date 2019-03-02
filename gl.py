def _init():
    global _global_dict
    _global_dict = {}


def set_value(name, value):
    _global_dict[name] = value


def get_value(name, def_value=None):
    try:
        return _global_dict[name]
    except KeyError:
        return def_value

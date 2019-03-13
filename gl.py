from PyQt5.QtCore import *
signals = None


class GlSignals(QObject):
    value_changed = pyqtSignal(dict)


def _init():
    global _global_dict, signals
    _global_dict = {}
    signals = GlSignals()


def set_value(name, value):
    change = {'name': name, 'new': value}
    if name in _global_dict:
        change['old'] = _global_dict[name]
        change['type'] = 'change'
    else:
        change['old'] = None
        change['type'] = 'add'
    _global_dict[name] = value
    signals.value_changed.emit(change)


def get_value(name, def_value=None):
    try:
        return _global_dict[name]
    except KeyError:
        return def_value

from PyQt5.QtCore import *
signals = None


class GlSignals(QObject):
    value_changed = pyqtSignal(str)


def _init():
    global _global_dict, signals
    _global_dict = {}
    signals = GlSignals()


def set_value(name, value):
    _global_dict[name] = value
    signals.value_changed.emit(str(name))


def get_value(name, def_value=None):
    try:
        return _global_dict[name]
    except KeyError:
        return def_value

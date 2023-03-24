import sys as _sys


# taken from the typing module.
def _caller(depth=1, default='__main__'):
    try:
        return _sys._getframe(depth + 1).f_globals.get('__name__', default)
    except (AttributeError, ValueError):  # For platforms without _getframe()
        return None

__version__ = "3.0.0-INDEV-PUBLIC-ALPHA"

__all__ = [
    "__version__"
]
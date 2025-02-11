from collections.abc import Callable, Iterable
from typing import Union

from .util import as_dataclass, to_camel_case, to_snake_case


class Callback:
    """Adds support for callbacks"""

    def __init__(self):
        """list of current callbacks"""

        self._callbacks = list()

    def get(self) -> list:
        """returns a list of registered events"""

        return [to_camel_case(fn.__name__[2:]) for fn in self._callbacks]

    def trigger(self, event, data):
        """trigger callback on event"""

        for fn in self._callbacks:
            if fn.__name__ == f"on_{to_snake_case(event)}":
                fn(as_dataclass(event, data))

    def register(self, fns: Union[Iterable, Callable]):
        """registers callback functions"""

        try:
            iterator = iter(fns)
            for fn in iterator:
                if fn not in self._callbacks:
                    self._callbacks.append(fn)
        except TypeError:
            if fns not in self._callbacks:
                self._callbacks.append(fns)

    def deregister(self, fns: Union[Iterable, Callable]):
        """deregisters callback functions"""

        try:
            iterator = iter(fns)
            for fn in iterator:
                if fn in self._callbacks:
                    self._callbacks.remove(fn)
        except TypeError:
            if fns in self._callbacks:
                self._callbacks.remove(fns)

    def clear(self):
        """clears the _callbacks list"""

        self._callbacks.clear()

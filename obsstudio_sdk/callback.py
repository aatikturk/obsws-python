import re
from typing import Callable, Iterable, Union


class Callback:
    """Adds support for callbacks"""

    def __init__(self):
        """list of current callbacks"""

        self._callbacks = list()

    def to_camel_case(self, s):
        s = "".join(word.title() for word in s.split("_"))
        return s[2:]

    def to_snake_case(self, s):
        s = re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
        return f"on_{s}"

    def get(self) -> list:
        """returns a list of registered events"""

        return [self.to_camel_case(fn.__name__) for fn in self._callbacks]

    def trigger(self, event, data):
        """trigger callback on update"""

        for fn in self._callbacks:
            if fn.__name__ == self.to_snake_case(event):
                fn(data.get("eventData"))

    def register(self, fns: Union[Iterable, Callable]):
        """registers callback functions"""

        try:
            iterator = iter(fns)
            for fn in iterator:
                if fn not in self._callbacks:
                    self._callbacks.append(fn)
        except TypeError as e:
            if fns not in self._callbacks:
                self._callbacks.append(fns)

    def deregister(self, callback):
        """deregisters a callback from _callbacks"""

        try:
            self._callbacks.remove(callback)
        except ValueError:
            print(f"Failed to remove: {callback}")

    def clear(self):
        """clears the _callbacks list"""

        self._callbacks.clear()

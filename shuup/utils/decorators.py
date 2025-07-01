import functools
import traceback


def non_reentrant(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        name = func.__name__
        if not hasattr(self, "_non_reentrant_check"):
            self._non_reentrant_check = {}
        invocation_stack = self._non_reentrant_check.get(name)
        if invocation_stack:
            msg = f"Error! Trying to re-entrantly call {name}. Last invocation was"
            stack_lines = traceback.format_list(invocation_stack)
            raise RuntimeError(msg, stack_lines)
        self._non_reentrant_check[name] = traceback.extract_stack()
        try:
            return func(self, *args, **kwargs)
        finally:
            del self._non_reentrant_check[name]

    return wrapped

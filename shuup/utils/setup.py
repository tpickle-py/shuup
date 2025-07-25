class Setup:
    def __init__(self, load_from=None):
        self.commit(load_from)

    def is_valid_key(self, key):
        return key == key.upper() and not key.startswith("_")

    def commit(self, source):
        if source:
            if not hasattr(source, "items"):  # pragma: no cover
                source = vars(source)
            for key, value in source.items():
                if self.is_valid_key(key):
                    setattr(self, key, value)

    def values(self):
        for key, value in self.__dict__.items():
            if self.is_valid_key(key):  # pragma: no branch
                yield (key, value)

    def get(self, key, default=None):  # pragma: no cover
        return getattr(self, key, default)

    def getlist(self, key, default=()):  # pragma: no cover
        val = getattr(self, key, default)
        return list(val)

    @classmethod
    def configure(cls, configure):
        setup = cls()
        try:
            configure(setup)
        except Exception:  # pragma: no cover
            print("@" * 80)  # noqa
            import sys
            import traceback

            traceback.print_exc()
            print("@" * 80)  # noqa
            sys.exit(1)
        return setup.values()

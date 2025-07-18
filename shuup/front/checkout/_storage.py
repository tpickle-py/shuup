class CheckoutPhaseStorage:
    def __init__(self, request, phase_identifier):
        self.request = request
        self.phase_identifier = phase_identifier
        self._key_prefix = f"checkout_{phase_identifier}:"

    def reset(self):
        keys_to_pop = {self._key_prefix + key for key in self.keys()}
        for key in keys_to_pop:
            self.request.session.pop(key, None)

    def set(self, key, value):
        self.request.session[self._key_prefix + key] = value

    def get(self, key, default=None):
        return self.request.session.get(self._key_prefix + key, default)

    def keys(self):
        key_prefix_len = len(self._key_prefix)
        for key in self.request.session.keys():
            if key.startswith(self._key_prefix):
                yield key[key_prefix_len:]

    def has_all(self, keys):
        return all(self.get(key) for key in keys)

    def has_any(self, keys):
        return any(self.get(key) for key in keys)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

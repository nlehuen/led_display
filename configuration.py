import json

NOTHING = object()

class Configuration(object):
    @classmethod
    def load(clazz, filename):
        with open(filename) as configuration_file:
            return Configuration(None, None, json.load(configuration_file))

    def __init__(self, parent, name, value):
        self._parent = parent
        self._name = name
        self._value = value

    def __getitem__(self, key):
        if isinstance(self._value, dict):
            try:
                return Configuration(self, key, self._value[key])
            except KeyError:
                pass
        return Configuration(self, key, NOTHING)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __name(self):
        result = []
        node = self
        while node is not None:
            if node._name is not None:
                result.insert(0, node._name)
            node = node._parent
        return '.'.join(result)

    def __iter__(self):
        if self._value is NOTHING:
            return
        if isinstance(self._value, list):
            for i, v in enumerate(self._value):
                yield i, Configuration(self, str(i), v)
        if isinstance(self._value, dict):
            for k, v in self._value.iteritems():
                yield k, Configuration(self, k, v)

    def value(self, default=None):
        if self._value is NOTHING:
            return default
        return self._value

    def required(self):
        if self._value is NOTHING:
            raise Exception("%s is a required parameter" % self.__name())
        return self._value

    def exists(self):
        return self._value is not NOTHING

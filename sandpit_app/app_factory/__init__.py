import importlib

class FactoryIndex(object):
    def __init__(self):
        factory_classes = [
            'web.python.Shykes',
            'web.java.UploadedWar'
        ]
        self.factories = dict((c, self._load_factory(c)) for c in factory_classes)

    def _load_factory(self, factory_type):
        factory_split = factory_type.split('.')
        factory_class = factory_split.pop()
        module = '.'.join(factory_split)

        m = importlib.import_module("app_factory." + module)
        factory = getattr(m, factory_class)

        return factory

    def app_types(self):
        return sorted([{'id': k, 'name':v.name} for k, v in self.factories.iteritems()], key=lambda x: x['name'])

    def get(self, app_type):
        return self.factories[app_type]


index = FactoryIndex()
'''
Smart trainer plugin loader
'''
import os
import logging

from motivation.trainers import SmartTrainer

LOGGER = logging.getLogger(__name__)


class TrainerPluginLoader:
    '''
    Plugin loader for smart trainer plugins
    '''

    _instance = None

    def __init__(self):
        self._plugins = []
        self._load_trainers()

    @classmethod
    def create(cls):
        '''
        Create an instance of the trainer plugin loader
        '''
        ldr = cls()
        TrainerPluginLoader._instance = ldr
        return ldr

    @classmethod
    def get(cls):
        '''
        Get or create an instance of the trainer plugin loader
        '''
        return cls._instance or cls.create()

    def __len__(self):
        return len(self._plugins)

    def __iter__(self):
        return iter(self._plugins)

    def get_by_uuid(self, trainer_uuid):
        '''
        Get a trainer plugin by Bluetooth GATT server UUID
        '''
        for plugin in self._plugins:
            if plugin.DEVICE_UUID == trainer_uuid:
                return plugin
        return None

    def is_supported_device(self, trainer_uuid):
        '''
        Determine if a device is supported by UUID
        '''
        return self.get_by_uuid(trainer_uuid) is not None

    def _load_trainers(self):
        '''
        Load the available trainer plugins
        '''
        import importlib
        import inspect

        plugin_path = os.path.abspath(os.path.dirname(__file__))
        plugin_path = os.path.join(plugin_path, "trainers")

        for module in os.listdir(plugin_path):
            fullpath = os.path.join(plugin_path, module)

            if module == "__init__.py":
                continue  # Skip
            if os.path.isdir(fullpath):
                continue  # Skip

            modname = '.trainers.' + os.path.splitext(module)[0]
            try:
                mod = importlib.import_module(modname, __package__)
            except Exception as e:  # pragma: no cover
                LOGGER.exception(f"Error: failed to load trainer plugin {modname}: {e}")
                continue

            for _, cls in inspect.getmembers(mod, inspect.isclass):
                if issubclass(cls, SmartTrainer) and cls is not SmartTrainer and cls not in self._plugins:
                    LOGGER.debug(f"Found trainer class {cls.__name__}")
                    self._plugins.append(cls)

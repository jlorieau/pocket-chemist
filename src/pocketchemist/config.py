"""
application configurations settings
"""
import yaml
import logging
from pathlib import Path
from importlib.metadata import entry_points  # python >=3.8
import collections.abc

config = {
    'config': {
        'file': '~/.pocketchemistrc'
    },
    'cli': {
        'color': True
    },
}

# Implementation for loading configs from different places

def recursive_update(d, u):
    """Recursively update a dict."""
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

# load plugins configs
for entrypoint in entry_points()['pocketchemist']:
    if entrypoint.name == 'config':
        try:
            plugin_config = entrypoint.load()
            recursive_update(config, plugin_config)
        except ModuleNotFoundError:
            logging.warning(f"The module '{entrypoint.value}' could not be "
                            f"found.")


# Load system config options
for filepath in (Path.home() / config['config']['file'],):
    if not filepath.exists():
        continue
        system_config = yaml.load(filepath)
        recursive_update(config, system_config)

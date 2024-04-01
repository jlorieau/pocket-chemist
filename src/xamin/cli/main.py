import sys

import click
import pluggy
from loguru import logger

from . import hookspecs, setup


def get_plugin_manager():
    """Retrieve and setup the plugin manager"""
    pm = pluggy.PluginManager("xamin")
    pm.add_hookspecs(hookspecs)  # Load this package's hookspecs
    pm.load_setuptools_entrypoints("xamin")  # Load plugin hookspecs
    pm.register(setup)
    return pm


def get_root_command():
    """Generate the root CLI command"""
    pm = get_plugin_manager()

    @click.group()
    @click.option('--debug', is_flag=True, default=False,
                  help="Display debugging information")
    def root_command(debug):
        """Xamin (examine) spectra and molecules"""
        # Remove default logger
        logger.remove()

        # Configure logger and set default level
        if debug:
            logger.add(sys.stderr, level="DEBUG", enqueue=True)
            logger.debug("Debug mode ON")
        else:
            logger.add(sys.stderr, level="WARNING", enqueue=True)

    # Add subcommands with plugins
    results = pm.hook.add_command(root_command=root_command)

    return root_command


def main():
    """The CLI entrypoint"""
    # Run the root command
    root_command = get_root_command()
    root_command()

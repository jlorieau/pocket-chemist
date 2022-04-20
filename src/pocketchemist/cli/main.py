import sys

import click
import pluggy
from loguru import logger

from . import hookspecs, setup


def get_plugin_manager():
    """Retrieve and setup the plugin manager"""
    pm = pluggy.PluginManager("pocketchemist")
    pm.add_hookspecs(hookspecs)  # Load this package's hookspecs
    pm.load_setuptools_entrypoints("pocketchemist")  # Load plugin hookspecs
    pm.register(setup)
    return pm


def main():
    """The CLI entrypoint"""
    pm = get_plugin_manager()

    @click.group()
    @click.option('--debug', is_flag=True, default=False,
                  help="Display debugging information")
    def root_command(debug):
        """A pocket chemist to analyze spectra and molecules"""
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

    # Run the root command
    root_command()

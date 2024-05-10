import sys

import click
import pluggy
from loguru import logger

from . import hookspecs, setup, gui


def get_plugin_manager():
    """Retrieve and setup the plugin manager"""
    pm = pluggy.PluginManager("xamin")
    pm.add_hookspecs(hookspecs)  # Load this package's hookspecs
    pm.load_setuptools_entrypoints("xamin")  # Load plugin hookspecs
    pm.register(setup)
    pm.register(gui)
    return pm


def get_root_command():
    """Generate the root CLI command"""
    pm = get_plugin_manager()

    @click.group()
    @click.option(
        "--debug", is_flag=True, default=False, help="Display debugging information"
    )
    def root_command(debug):
        """(e)Xamin spectra and molecules"""
        # Remove default logger
        logger.remove()

        # Configure logger and set default level
        if debug:
            logger.add(sys.stderr, level="DEBUG", enqueue=True, backtrace=False)
            logger.debug("Debug mode ON")
        else:
            logger.add(sys.stderr, level="WARNING", enqueue=True, backtrace=False)

        # Catch exceptions and log them
        def excepthook(exc_type, exc_value, exc_traceback):
            """Catch and log exceptions, then continue"""
            # Allow Ctrl+C to exit from the terminal
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return None

            # Log the error and do nothing
            logger.opt(exception=(exc_type, exc_value, exc_traceback)).error(
                "Exception"
            )

        # Set the global exception catching hook to use the logger
        sys.excepthook = excepthook

    # Add subcommands with plugins
    results = pm.hook.add_command(root_command=root_command)

    return root_command


def main():
    """The CLI entrypoint"""
    # Run the root command
    root_command = get_root_command()
    root_command()

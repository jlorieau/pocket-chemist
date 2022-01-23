from importlib.metadata import entry_points  # python >=3.8
import sys

import click
from loguru import logger

from .setup import setup


@click.group()
@click.option('--debug', is_flag=True, default=False,
              help="Display debugging information")
def main(debug):
    """A pocket chemist to analyze spectra and molecules"""
    # Remove default logger
    logger.remove()

    # Configure logger and set default level
    if debug:
        logger.add(sys.stderr, level="DEBUG", enqueue=True)
        logger.debug("Debug mode ON")
    else:
        logger.add(sys.stderr, level="WARNING", enqueue=True)


# Add subcommands
main.add_command(setup)


# load plugins
for entrypoint in entry_points().get('pocketchemist', []):
    if entrypoint.name == 'cli':
        try:
            main.add_command(entrypoint.load())
        except ModuleNotFoundError:
            logger.warning(f"The module '{entrypoint.value}' could not be "
                           f"found.")


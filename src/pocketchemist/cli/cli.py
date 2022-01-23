from importlib.metadata import entry_points  # python >=3.8
import logging

import click
import coloredlogs

from .setup import setup

logger = logging.getLogger('pocketchemist.cli.cli')


@click.group()
@click.option('--debug', is_flag=True, default=False,
              help="Display debugging information")
def main(debug):
    """A pocket chemist to analyze spectra and molecules"""
    # Setup logging
    if debug:
        coloredlogs.install(level='DEBUG')
        logging.basicConfig()
        logger.debug("Debugging mode turned ON")
    else:
        coloredlogs.install(level='WARNING')


# Add subcommands
main.add_command(setup)


# load plugins
for entrypoint in entry_points().get('pocketchemist', []):
    if entrypoint.name == 'cli':
        try:
            main.add_command(entrypoint.load())
        except ModuleNotFoundError:
            logging.warning(f"The module '{entrypoint.value}' could not be "
                            f"found.")


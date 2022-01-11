from importlib.metadata import entry_points  # python >=3.8
import logging

import click
import coloredlogs


@click.group()
@click.option('--debug', is_flag=True, default=False,
              help="Display debugging information")
def pocketchemist(debug):
    """A pocket chemist to analyze spectra and molecules."""
    # Setup logging
    if debug:
        coloredlogs.install(level='DEBUG')
        logging.basicConfig()
        logging.debug("Debuggin mode turned ON")
    else:
        coloredlogs.install(level='WARNING')


# load plugins
for entrypoint in entry_points()['pocketchemist']:
    pocketchemist.add_command(entrypoint.load())

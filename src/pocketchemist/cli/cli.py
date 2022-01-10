from importlib.metadata import entry_points  # python >=3.8
import logging

import click


@click.group()
@click.option('--debug', is_flag=True, default=False,
              help="Display debugging information")
def pocketchemist(debug):
    """A pocket chemist to analyze spectra and molecules."""
    # Turn on debugging, if specified
    if debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debuggin mode turned ON")

# load plugins
for entrypoint in entry_points()['pocketchemist']:
    pocketchemist.add_command(entrypoint.load())

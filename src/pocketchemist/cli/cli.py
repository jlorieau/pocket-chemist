from importlib.metadata import entry_points  # python >=3.8
import logging

import click
import coloredlogs
import yaml

from ..config import config as config_dict


@click.group()
@click.option('--debug', is_flag=True, default=False,
              help="Display debugging information")
def main(debug):
    """A pocket chemist to analyze spectra and molecules"""
    # Setup logging
    if debug:
        coloredlogs.install(level='DEBUG')
        logging.basicConfig()
        logging.debug("Debuggin mode turned ON")
    else:
        coloredlogs.install(level='WARNING')


@main.command()
def config():
    """Display and save the current configuration settings"""
    string = yaml.safe_dump(config_dict)
    print(string)


# load plugins
for entrypoint in entry_points()['pocketchemist']:
    if entrypoint.name == 'cli':
        try:
            main.add_command(entrypoint.load())
        except ModuleNotFoundError:
            logging.warning(f"The module '{entrypoint.value}' could not be "
                            f"found.")


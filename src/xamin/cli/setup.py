"""
Setup CLI subcommand
"""

from inspect import isabstract
from itertools import groupby

import click

from .main import xamin
from ..processors import Processor
from ..utils.classes import all_subclasses


@xamin.group()
def setup():
    """Print information on the current setup"""
    pass


@setup.command()
@click.option(
    "--only-concrete",
    is_flag=True,
    default=False,
    help="Only show concrete (non-abstract) classes",
)
def processors(only_concrete):
    """List the available processors"""
    # Retrieve a list of all processor classes
    processor_clses = all_subclasses(Processor)

    # Retrieve only concrete classes--remove abstract classes--if specified
    if only_concrete:
        processor_clses = [
            processor_cls
            for processor_cls in processor_clses
            if isabstract(processor_cls)
        ]

    for count, processor_cls in enumerate(processor_clses, 1):
        click.echo(f"{count}. {processor_cls}")

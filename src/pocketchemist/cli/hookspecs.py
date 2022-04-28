"""
Specifications for plugin hooks
"""
import click

from ..hookspecs import hookspec


@hookspec
def add_command(root_command: click.Command):
    """A a click command to the command-line interface (CLI)

    Parameters
    ----------
    root_command
        The root command to add the command or command group to.
    """

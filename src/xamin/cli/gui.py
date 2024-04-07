"""Click interface for gui"""

import click
from ..hookimpls import xamin


@xamin
def add_command(root_command):
    """Plugin hook to add the gui cli sub-command"""
    root_command.add_command(gui)


@click.command()
@click.argument("args", nargs=-1)
def gui(args):
    """The graphical user interface (GUI) arguments"""
    from ..gui import MainApplication, MainWindow

    # Create the root app
    app = MainApplication(list(args))

    # Create the main window
    window = MainWindow(*args)
    window.show()

    # Show the window and start root app
    app.exec()

"""Click interface for gui"""

import click

from .main import xamin


@xamin.command()
@click.argument("args", nargs=-1)
def gui(args: tuple[str]) -> None:
    """The graphical user interface (GUI) arguments"""
    from ..gui import MainApplication, MainWindow

    # Create the root app
    app = MainApplication(list(args))

    # Create the main window
    window = MainWindow()
    window.show()

    # Show the window and start root app

    app.exec()

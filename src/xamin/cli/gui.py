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
    from ..gui import MainWindow
    from PyQt6.QtWidgets import QApplication
    from loguru import logger

    logger.debug(f"args: {args}")
    # Create the root app
    app = QApplication(list(args))

    # Set style
    app.setStyle("Fusion")
    # Create the main window
    window = MainWindow(*args)
    window.show()

    # Show the window and start root app
    app.exec()

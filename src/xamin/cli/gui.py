"""Click interface for gui"""

import click
from loguru import logger

from ..hookimpls import xamin


@xamin
def add_command(root_command):
    """Plugin hook to add the gui cli sub-command"""
    root_command.add_command(gui)


@click.command()
@click.argument("args", nargs=-1)
def gui(args):
    """The graphical user interface (GUI) arguments"""
    import sys
    from ..gui import MainApplication, MainWindow

    # Disable showing backtrace to stdout
    logger.remove()
    logger.add(sys.stderr, backtrace=False)

    def excepthook(exc_type, exc_value, exc_traceback):
        """Catch and log exceptions, then continue"""
        # Allow Ctrl+C to exit from the terminal
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return None

        # Log the error and do nothing
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).error("Exception")

    # Set the global exception catching hook to use the logger
    sys.excepthook = excepthook

    # Create the root app
    app = MainApplication(list(args))

    # Create the main window
    window = MainWindow(*args)
    window.show()

    # Show the window and start root app

    app.exec()

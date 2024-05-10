import sys

import click
from loguru import logger


__all__ = ("xamin",)


@click.group()
@click.option(
    "--debug", is_flag=True, default=False, help="Display debugging information"
)
def xamin(debug):
    """(e)Xamin spectra and molecules"""
    # Remove default logger
    logger.remove()

    # Configure logger and set default level
    if debug:
        logger.add(sys.stderr, level="DEBUG", enqueue=True, backtrace=False)
        logger.debug("Debug mode ON")
    else:
        logger.add(sys.stderr, level="WARNING", enqueue=True, backtrace=False)

    # Catch exceptions and log them
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


def main():
    """The CLI entrypoint"""
    # Run the root command
    xamin()

"""Module to create a custom logger for the application."""

import logging


class CustomLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR', including traceback information.
        """
        kwargs.setdefault("exc_info", True)
        super(CustomLogger, self).error(msg, *args, **kwargs)


logging.setLoggerClass(CustomLogger)

if True:
    logLevel = logging.INFO

logging.basicConfig(
    format="%(levelname)-4s:  %(filename)12.12s:%(lineno)3d - %(message)s",
    level=logLevel,
)

log = logging.getLogger(__name__)

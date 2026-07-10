import logging
import os
from logging.handlers import RotatingFileHandler
from bms.controller import BASEDIR

class Logger:
    def __init__(self, name, log_file=f"{BASEDIR}/loggers/app.log",
                 max_bytes=10*1024*1024, backup_count=2, console=False):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        if not self._logger.handlers:
            formatter = logging.Formatter(
                '[%(levelname)s] %(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(message)s'
            )
            handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

            if console:
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(logging.DEBUG)
                stream_handler.setFormatter(formatter)
                self._logger.addHandler(stream_handler)

    def debug(self, msg):
        self._logger.debug(msg, stacklevel=2)

    def info(self, msg):
        self._logger.info(msg, stacklevel=2)

    def warning(self, msg):
        self._logger.warning(msg, stacklevel=2)

    def error(self, msg, exc_info=False):
        self._logger.error(msg, exc_info=exc_info, stacklevel=2)

    def critical(self, msg, exc_info=False):
        self._logger.critical(msg, exc_info=exc_info, stacklevel=2)


logger = Logger("backend", log_file=f"{BASEDIR}/loggers/backend_log.log",
                 max_bytes=10*1024*1024, backup_count=2)
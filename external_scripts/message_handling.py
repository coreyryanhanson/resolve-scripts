"""A module to simplify the creation of logging objects and managing
verbosity."""


import logging
import functools
from typing import Optional
from threading import Lock
from warnings import warn


class LoggerGenerator:
    """Custom class to streamline the creation of logging objects.

    Args:
        log_filepath (str): The filepath to the log file.
        logger_name (Optional[str], optional): The name to assign to the new
            logger. If none, it will be assigned the name "messagehandler."
            Defaults to None.
    """
    def __init__(self,
                 log_filepath: str,
                 logger_name: Optional[str] = None
                 ) -> None:
        self._logger = self._create_logger(logger_name)
        self._handler = self._create_file_handler(log_filepath)
        self.default_format = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

    def _create_logger(self,
                       logger_name: Optional[str] = None
                       ) -> logging.Logger:
        if not logger_name:
            logger_name = "messagehandler"
        return logging.getLogger(logger_name)

    def _create_file_handler(self, log_filepath: str) -> logging.FileHandler:
        return logging.FileHandler(log_filepath)

    def _parse_logger_level(self, level_str: Optional[str] = None) -> int:
        if not level_str:
            return logging.INFO
        level_str = level_str.lower()
        if level_str == "debug":
            return logging.DEBUG
        if level_str == "info":
            return logging.INFO
        if level_str == "warning":
            return logging.WARNING
        if level_str == "error":
            return logging.ERROR
        if (level_str == "critical") or (level_str == "fatal"):
            return logging.CRITICAL
        raise ValueError("Invalid option for logger level.")

    def _set_logger_level(self, level_str: Optional[str] = None) -> None:
        level = self._parse_logger_level(level_str)
        for item in [self._logger, self._handler]:
            item.setLevel(level)

    def _apply_formatting(self, logger_format: Optional[str] = None) -> None:
        logger_format = logger_format if logger_format else self.default_format
        formatter = logging.Formatter(logger_format)
        self._handler.setFormatter(formatter)

    def generate(self,
                 logger_level: Optional[str] = None,
                 logger_format: Optional[str] = None
                 ) -> logging.Logger:
        """Configures the logging options for the logging object.

        Args:
            logger_level (Optional[str], optional): The level of logging
                messages. If None the level will be set to "info." Defaults to
                None.
            logger_format (Optional[str], optional): The formatting string that
                determines the displayed log messages. If none defaults to the
                format stored in self.default_format. Defaults to None.

        Returns:
            logging.Logger: A connected logging object.
        """
        self._set_logger_level(logger_level)
        self._apply_formatting(logger_format)
        self._logger.addHandler(self._handler)
        return self._logger


class MessageHandlingObject:
    """A base class to with convenience methods that integrate various levels
    of logging and verbosity.

    Args:
        verbose (bool, optional): Whetther to show print statements. Does not
            affect logs. Defaults to False.
        suppress_warnings (bool, optional): Whether to suppress warnings. Does
            not affect logs. Defaults to False.
        log_filepath (Optional[str]): The filepath to the log file. Provide
            this if you would like to generate a new logging object. Defaults
            to None.
        logger_name (Optional[str], optional): The name to assign to the new
            logger if one is being generated. If none, it will be assigned the
            name "messagehandler." Defaults to None.
        logger_level (Optional[str], optional): The level of logging
            messages. If None and a mew ;pgger os being created the level will
            be set to "info." Defaults to None.
        logger_format (Optional[str], optional): The formatting string that
            determines the displayed log messages. If none and a new logger is
            being created, it will default to the format stored in
            self.default_format in the LoggerGenerator class. Defaults to None.
        shared_logger (Optional[logging.Logger], optional): Add an existing
            logging object here. If not provided either a new one will be
            generated or logging will be disabled depending on the other
            argument choices. Defaults to None.
    """
    def __init__(self,
                 verbose: bool = False,
                 suppress_warnings: bool = False,
                 log_filepath: Optional[str] = None,
                 logger_name: Optional[str] = None,
                 logger_level: Optional[str] = None,
                 logger_format: Optional[str] = None,
                 shared_logger: Optional[logging.Logger] = None
                 ) -> None:
        self._verbose = verbose
        self._suppress_warnings = suppress_warnings
        self._logger = self._init_logger(log_filepath,
                                         logger_name,
                                         logger_level,
                                         logger_format,
                                         shared_logger)
        self._use_threaded_log_locks = False
        self._log_lock = Lock()

    def _locked_log_process(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            locked = self._use_threaded_log_locks
            if locked:
                self._log_lock.acquire()
            output = func(self, *args, **kwargs)
            if locked:
                self._log_lock.release()
            return output
        return wrapper

    def _init_logger(self,
                     log_filepath: Optional[str] = None,
                     logger_name: Optional[str] = None,
                     logger_level: Optional[str] = None,
                     logger_format: Optional[str] = None,
                     shared_logger: Optional[logging.Logger] = None
                     ) -> Optional[logging.Logger]:
        if shared_logger is not None and any([log_filepath,
                                              logger_name,
                                              logger_level,
                                              logger_format]):
            raise ValueError("Must choose between providing an existing "
                             "logger or specify itialization arguments. "
                             "Cannot do both.")
        if shared_logger is None:
            if log_filepath is None:
                return None
            logger_generator = LoggerGenerator(log_filepath, logger_name)
            return logger_generator.generate(logger_level, logger_format)
        return shared_logger

    @_locked_log_process
    def _print(self, string, **kwargs):
        if self._verbose:
            print(string, **kwargs)
        if self._logger is not None:
            self._logger.info(string)

    @_locked_log_process
    def _warn(self, string):
        if not self._suppress_warnings:
            warn(string)
        if self._logger is not None:
            self._logger.warning(string)

    @_locked_log_process
    def _raise(self, error):
        if self._logger is not None:
            self._logger.exception(error)
        raise error

    def set_logger(self,
                   log_filepath: Optional[str] = None,
                   logger_name: Optional[str] = None,
                   logger_level: Optional[str] = None,
                   logger_format: Optional[str] = None,
                   shared_logger: Optional[logging.Logger] = None
                   ) -> None:
        """Sets the objects logger either by passing an existing log object or
        generating a new one. If log_filepath and shared_logger are both
        empty, logging functionality will be disabled.

        Args:
            log_filepath (Optional[str]): The filepath to the log file. Provide
                this if you would like to generate a new logging object.
                Defaults to None.
            logger_name (Optional[str], optional): The name to assign to the
                new logger if one is being generated. If none, it will be
                assigned the default name in the LoggerGenerator class.
                Defaults to None.
            logger_level (Optional[str], optional): The level of logging
                messages. If None and a mew ;pgger os being created the level
                will be set to "info." Defaults to None.
            logger_format (Optional[str], optional): The formatting string that
                determines the displayed log messages. If none and a new
                logger is being created, it will default to the format stored
                in self.default_format in the LoggerGenerator class. Defaults
                to None.
            shared_logger (Optional[logging.Logger], optional): Add an existing
                logging object here. If not provided either a new one will be
                generated or logging will be disabled depending on the other
                argument choices. Defaults to None.
        """
        self._logger = self._init_logger(log_filepath,
                                         logger_name,
                                         logger_level,
                                         logger_format,
                                         shared_logger)


def main():
    first = MessageHandlingObject(log_filepath="test.log",
                                  logger_name="testing")
    handler = MessageHandlingObject(verbose=True,
                                    suppress_warnings=False,
                                    shared_logger=first._logger)
    handler._print("Info text")
    handler._warn("Warning text")
    handler._raise(ValueError("An error"))


if __name__ == "__main__":
    main()

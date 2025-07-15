import logging

class LogFormatters():
    """Collection of different log formatters for various purposes"""

    @staticmethod
    def get_console_formatter():

        return logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )

    @staticmethod
    def get_file_formatter():
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    @staticmethod
    def get_error_formatter():
        """Special formatter for error logs - includes all context."""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    @staticmethod
    def get_json_formatter():
        """JSON formatter for machine processing """
        return logging.Formatter(
            '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "module": "%(module)s", "line": %(lineno)d, "message": "%(message)s"}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
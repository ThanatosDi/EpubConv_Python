import logging
import logging.config
import os
import sys

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


class Logger(object):
    """Logger
    Logger level:
        CRITICAL    50
        ERROR	    40
        WARNING	    30
        INFO	    20
        DEBUG	    10
        NOTSET	     0
    """

    # def __init__(self, name='logger', level=logging.DEBUG):
    # logging.basicConfig(format='%(asctime)s %(levelname)s :\n%(message)s',
    #                    level=level, datefmt='%Y-%m-%d %H:%M:%S', filename='DB_API.log', filemode='w')

    def __init__(self, name='logger', filehandler='INFO', streamhandler='INFO', workPath=None):
        """Logger
        Keyword Arguments:
            name {str} -- [name of logging] (default: {'logger'})
        """

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s %(name)-8s %(levelname)-8s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        if not workPath:
            workPath = os.path.abspath(
                os.path.join(sys.argv[0], os.path.pardir))

        # log 檔案 handler
        file_handler = logging.handlers.TimedRotatingFileHandler(
            f'{workPath}/storages/logs/app.log', encoding='utf-8', when='D', backupCount=3)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, filehandler.upper()))

        # stdout handler
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(formatter)
        self.stream_handler.setLevel(getattr(logging, streamhandler.upper()))

        if not self.logger.hasHandlers():
            self.logger.addHandler(file_handler)
            self.logger.addHandler(self.stream_handler)

    def level_color(self, level):
        default_color = {
            'WARNING': MAGENTA,
            'INFO': GREEN,
            'DEBUG': CYAN,
            'CRITICAL': YELLOW,
            'ERROR': RED
        }
        color = default_color.get(level.upper(), WHITE)
        formatter = f'%(asctime)s %(name)-8s {COLOR_SEQ % (30+color)}%(levelname)-8s{RESET_SEQ} : %(message)s'
        return formatter

    def debug(self, msg):
        """ logging debug level
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        formatter = logging.Formatter(self.level_color(
            'debug'), datefmt='%Y-%m-%d %H:%M:%S')
        self.stream_handler.setFormatter(formatter)
        self.logger.debug(msg)

    def info(self, msg):
        """ logging info level
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        formatter = logging.Formatter(self.level_color(
            'info'), datefmt='%Y-%m-%d %H:%M:%S')
        self.stream_handler.setFormatter(formatter)
        self.logger.info(msg)

    def warning(self, msg):
        """ logging warning level
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        formatter = logging.Formatter(self.level_color(
            'warning'), datefmt='%Y-%m-%d %H:%M:%S')
        self.stream_handler.setFormatter(formatter)
        self.logger.warning(msg)

    def error(self, msg):
        """ logging error level
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        formatter = logging.Formatter(self.level_color(
            'error'), datefmt='%Y-%m-%d %H:%M:%S')
        self.stream_handler.setFormatter(formatter)
        self.logger.error(msg)

    def critical(self, msg):
        formatter = logging.Formatter(self.level_color(
            'critical'), datefmt='%Y-%m-%d %H:%M:%S')
        self.stream_handler.setFormatter(formatter)
        self.logger.critical(msg)

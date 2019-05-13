import logging
import time
import logging.config


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

    #def __init__(self, name='logger', level=logging.DEBUG):
        #logging.basicConfig(format='%(asctime)s %(levelname)s :\n%(message)s',
        #                    level=level, datefmt='%Y-%m-%d %H:%M:%S', filename='DBAPI.log', filemode='w')

    def __init__(self, name='logger'):
        """Logger
        
        Keyword Arguments:
            name {str} -- [name of logging] (default: {'logger'})
        """
        logging.config.fileConfig(fname='logging.conf', disable_existing_loggers=False)
        self.logger = logging.getLogger(name)

    def debug(self, function, msg):
        """ logging debug level
        
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        message = f" * function: {function}, * msg: {msg}"
        self.logger.debug(message)

    def info(self, function, msg):
        """ logging info level
        
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        message = f" * function: {function}, * msg: {msg}"
        self.logger.info(message)

    def warning(self, function, msg):
        """ logging warning level
        
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        message = f" * function: {function}, * msg: {msg}"
        self.logger.warning(message)

    def error(self, function, msg):
        """ logging error level
        
        Arguments:
            function {str} -- message of function
            msg {str} -- message
        """
        message = f" * function: {function}, * msg: {msg}"
        self.logger.error(message)

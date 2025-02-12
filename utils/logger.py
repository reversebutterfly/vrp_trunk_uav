import os
import logging
from logging.handlers import TimedRotatingFileHandler


PATH = os.path.dirname(os.path.dirname(__file__))


class Logger(object):
    """
    log writer
    """

    def __init__(self, log_name: str):
        """
        log writer, initialise

        :param log_name:  file name of log
        """

        self.log_name = log_name
        self.log = logging.getLogger(name=self.log_name)
        self.log.setLevel(logging.INFO)

        # initialise logging
        logging.basicConfig()

        # output format
        fmt_st = "%(asctime)s[%(levelname)s][%(processName)s][%(threadName)s]:%(message)s"
        formatter = logging.Formatter(fmt=fmt_st)

        # log file
        path_root = os.path.join(PATH, "log")  # root directory of log
        if not os.path.exists(path_root):
            os.makedirs(name=path_root)
        path = os.path.join(path_root, self.log_name)

        # level and format
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=path)
        file_handler.setLevel(level=logging.INFO)
        file_handler.setFormatter(fmt=formatter)
        self.log.addHandler(hdlr=file_handler)

    def info(self, msg: str):
        """
        info

        :param msg:  info

        :return: nothing
        """

        msg_ = " " + msg
        self.log.info(msg=msg_)

    def error(self, msg: str):
        """
        error info

        :param msg:  error info

        :return: nothing
        """

        msg_ = " " + msg
        self.log.error(msg=msg_)


log_tsp = Logger(log_name='tsp.log')
log_vrp = Logger(log_name='vrp.log')

import logging
import os


def get_logger_name():
    return os.getcwd().split("/")[-1]


logger = logging.getLogger(get_logger_name())
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch2 = logging.FileHandler(get_logger_name()+".log")
ch2.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

ch.setFormatter(formatter)
ch2.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(ch2)

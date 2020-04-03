import logging
import sys


def initialize_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(threadName)s (%(levelname)s): #%(lineno)d %(message)s'
    )

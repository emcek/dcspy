from datetime import datetime
from logging import DEBUG, StreamHandler, INFO, Formatter, Logger
from logging.handlers import RotatingFileHandler
from os import environ, path


def config_logger(logger: Logger) -> None:
    """
    Configure logger form dcspy, add handlers and set formatters.
    :param logger:
    :type: Logger
    """
    logger.setLevel(DEBUG)
    file_hand = RotatingFileHandler(filename=path.join(environ.get('TEMP', ''), 'dcspy.log'), mode='a', maxBytes=1024*1024, backupCount=1)
    file_hand.setLevel(DEBUG)
    stream_hand = StreamHandler()
    stream_hand.setLevel(INFO)
    file_format = Formatter('%(asctime)s | %(name)-17s | %(levelname)-7s | %(message)s / %(funcName)s:%(lineno)d')
    stream_format = Formatter('%(levelname)-7s | %(message)s')
    file_hand.setFormatter(file_format)
    stream_hand.setFormatter(stream_format)
    logger.addHandler(stream_hand)
    logger.addHandler(file_hand)
    header = '#' * 60
    logger.debug(f'\n{header}\nStart session: {datetime.now()}\n{header}')
    logger.info(f'Log file store at: {file_hand.baseFilename}')

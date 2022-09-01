from datetime import datetime
from logging import DEBUG, StreamHandler, INFO, Formatter, Logger
from logging.handlers import RotatingFileHandler
from os import path
from tempfile import gettempdir


def config_logger(logger: Logger, verbose=False) -> None:
    """
    Configure global logger add handlers and set formatters.

    :param logger:
    :param verbose: turn on/off verbose mode
    """
    logger.setLevel(DEBUG)
    file_hand = RotatingFileHandler(filename=path.join(gettempdir(), 'dcspy.log'), mode='a', encoding='utf-8', maxBytes=5 * 1024 * 1024, backupCount=1)
    file_hand.setLevel(DEBUG)
    file_hand.setFormatter(Formatter('%(asctime)s | %(name)-17s | %(levelname)-7s | %(threadName)-10s | %(message)s / %(funcName)s:%(lineno)d'))
    stream_hand = StreamHandler()
    stream_hand.setLevel(INFO)
    if verbose:
        stream_hand.setLevel(DEBUG)
    stream_hand.setFormatter(Formatter('%(levelname)-7s | %(message)s'))
    logger.addHandler(stream_hand)
    logger.addHandler(file_hand)
    header = '#' * 60
    logger.debug(f'\n{header}\nStart session: {datetime.now()}\n{header}')
    logger.info(f'Log file store at: {file_hand.baseFilename}')

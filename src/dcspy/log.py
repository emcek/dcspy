from datetime import datetime
from logging import DEBUG, INFO, Formatter, Handler, Logger, LogRecord, StreamHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tempfile import gettempdir
from typing import ClassVar

from PySide6.QtGui import QColorConstants, QTextCharFormat
from PySide6.QtWidgets import QTextEdit


def config_logger(logger: Logger, verbose: bool = False) -> None:
    """
    Configure global logger add handlers and set formatters.

    :param logger: Logger instance
    :param verbose: Turn on/off verbose mode
    """
    logger.setLevel(DEBUG)
    file_hand = RotatingFileHandler(filename=Path(gettempdir()) / 'dcspy.log', mode='a', encoding='utf-8', maxBytes=5 * 1024 * 1024, backupCount=1)
    file_hand.setFormatter(Formatter('%(asctime)s | %(name)-17s | %(levelname)-7s | %(threadName)-10s | %(message)s / %(funcName)s:%(lineno)d'))
    file_hand.setLevel(INFO)
    stream_hand = StreamHandler()
    stream_hand.setLevel(INFO)
    if verbose:
        file_hand.setLevel(DEBUG)
        stream_hand.setLevel(DEBUG)
    stream_hand.setFormatter(Formatter('%(levelname)-7s | %(message)s'))
    logger.addHandler(stream_hand)
    logger.addHandler(file_hand)
    header = '#' * 60
    logger.debug(f'\n{header}\nStart session: {datetime.now()}\n{header}')
    logger.info(f'Log file store at: {file_hand.baseFilename}')


class QTextEditLogHandler(Handler):
    """GUI log handler."""
    colors: ClassVar[dict[str, QColorConstants.Svg]] = {
        'DEBUG': QColorConstants.Svg.black,
        'INFO': QColorConstants.Svg.green,
        'WARNING': QColorConstants.Svg.darkorange,
        'ERROR': QColorConstants.Svg.red,
        'CRITICAL': QColorConstants.Svg.blue
    }

    def __init__(self, text_widget: QTextEdit) -> None:
        """
        Log handler for GUI application.

        :param text_widget: widget to emit logs to.
        """
        super().__init__()
        self.text_widget = text_widget
        self.paused = False

    def emit(self, record: LogRecord) -> None:
        """
        Emit a log record.

        :param record: LogRecord instance.
        """
        if self.paused:
            return
        cursor = self.text_widget.textCursor()
        text_format = QTextCharFormat()
        text_format.setForeground(self.colors.get(record.levelname, QColorConstants.Svg.black))
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(f'{self.format(record)}\n', text_format)
        self.text_widget.setTextCursor(cursor)
        self.text_widget.ensureCursorVisible()

    def toggle_logging(self, state: bool) -> None:
        """
        Toggle logging state on and off.

        :param state: State of logging
        """
        self.paused = state

import tkinter as tk
from logging import getLogger
from sys import prefix
from threading import Event

from dcspy import config, LCD_TYPES
from dcspy.starter import dcspy_run
from dcspy.tk_gui import DcspyGui

LOG = getLogger(__name__)
__version__ = '1.6.0'


def run():
    """Function to start DCSpy GUI."""
    if config['show_gui']:
        LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
        root = tk.Tk()
        width, height = 210, 160
        root.geometry(f'{width}x{height}')
        root.minsize(width=width, height=height)
        root.iconbitmap(f'{prefix}/dcspy_data/dcspy.ico')
        gui = DcspyGui(master=root, config_file=f'{prefix}/dcspy_data/config.yaml')
        gui.mainloop()
    else:
        dcspy_run(lcd_type=LCD_TYPES[config['keyboard']], event=Event())


if __name__ == '__main__':
    run()

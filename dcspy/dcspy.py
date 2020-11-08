import sys
import tkinter as tk
from logging import getLogger

from dcspy.tk_gui import DcspyGui

LOG = getLogger(__name__)
__version__ = '1.2.0'


def run():
    """Function to start DCSpy GUI."""
    LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
    root = tk.Tk()
    width, height = 200, 130
    root.geometry(f'{width}x{height}')
    root.minsize(width=width, height=height)
    root.iconbitmap(f'{sys.prefix}/dcspy_data/dcspy.ico')
    gui = DcspyGui(master=root)
    gui.mainloop()


if __name__ == '__main__':
    run()

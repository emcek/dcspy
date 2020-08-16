import sys
import tkinter as tk
from logging import getLogger

from dcspy.tk_gui import DcspyGui

LOG = getLogger(__name__)


def run():
    """Function to start DCSpy GUI."""
    root = tk.Tk()
    w, h = 150, 100
    root.geometry(f'{w}x{h}')
    root.minsize(w, h)
    root.iconbitmap(f'{sys.prefix}/dcspy_data/dcspy.ico')
    gui = DcspyGui(master=root)
    gui.mainloop()


if __name__ == '__main__':
    run()

import sys
import tkinter as tk
from logging import getLogger

LOG = getLogger(__name__)


def run():
    """Function to start DCSpy GUI."""
    root = tk.Tk()
    root.geometry('150x80')
    root.minsize(150, 80)
    root.iconbitmap(f'{sys.prefix}/dcspy_data/dcspy.ico')
    gui = DcspyGui(master=root)
    gui.mainloop()


if __name__ == '__main__':
    run()

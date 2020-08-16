import sys
import tkinter as tk
from logging import getLogger

LOG = getLogger(__name__)


def run():
    """Main of running function."""
    root = tk.Tk()
    root.geometry('150x80')
    root.minsize(150, 80)
    root.iconbitmap(f'{sys.prefix}/dcspy_data/dcspy.ico')
    gui = DcspyGui(master=root)
    gui.mainloop()


class DcspyGui(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()
        self.lcd_type = tk.StringVar()
        self._create_widgets()

    def _create_widgets(self):
        frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        lcd_types = {'G19': 'G19', 'G510': 'G510', 'G15 v1/v2': 'G15', 'G13': 'G13'}
        for text, value in lcd_types.items():
            rb = tk.Radiobutton(master=frame, text=text, variable=self.lcd_type, value=value, command=self.sel)
            rb.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
            rb.select()

        start = tk.Button(master=self.master, text='Start', command=DcspyGui.start_dcspy)
        close = tk.Button(master=self.master, text='Close', command=self.master.destroy)

        frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        start.pack(side=tk.TOP, fill=tk.X, expand=True)
        close.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    def sel(self):
        selection = 'You selected the option ' + self.lcd_type.get()
        print(selection)

    @staticmethod
    def start_dcspy():
        from dcspy import starter
        starter.run()


if __name__ == '__main__':
    run()

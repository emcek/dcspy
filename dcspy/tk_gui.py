import tkinter as tk
from logging import getLogger
from threading import Thread

from dcspy import starter

LOG = getLogger(__name__)


class DcspyGui(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        """
        Basic constructor.

        :param master: Top level widget
        """
        super().__init__(master)
        self.master = master
        self.master.title('dcspy')
        self.lcd_type = tk.StringVar()
        self.status_txt = tk.StringVar()
        self._init_widgets()

    def _init_widgets(self) -> None:
        self.master.columnconfigure(index=0, weight=1)
        self.master.columnconfigure(index=1, weight=1)
        self.master.rowconfigure(index=0, weight=1)
        self.master.rowconfigure(index=1, weight=1)
        self.master.rowconfigure(index=2, weight=1)

        frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        lcd_types = {'G19': 'G19', 'G510': 'G510', 'G15 v1/v2': 'G15', 'G13': 'G13'}
        for i, (text, value) in enumerate(lcd_types.items()):
            rb = tk.Radiobutton(master=frame, text=text, variable=self.lcd_type, value=value, command=self._lcd_type_selected)
            rb.grid(row=i, column=0, pady=0, padx=2, sticky=tk.W)
            rb.select()

        start = tk.Button(master=self.master, text='Start', command=self.start_dcspy)
        close = tk.Button(master=self.master, text='Close', command=self.master.destroy)
        status = tk.Label(master=self.master, textvariable=self.status_txt)

        frame.grid(row=0, column=0, padx=2, pady=2, rowspan=2)
        start.grid(row=0, column=1, padx=2, pady=2)
        close.grid(row=1, column=1, padx=2, pady=2)
        status.grid(row=2, column=0, columnspan=2, sticky=tk.W)

    def _lcd_type_selected(self) -> None:
        """Handling selected LCD type."""
        LOG.debug(f'Logitech {self.lcd_type.get()} selected')
        self.status_txt.set(f'Logitech {self.lcd_type.get()} selected')

    def start_dcspy(self) -> None:
        """Run real application."""
        t = Thread(target=starter.run)
        t.setName('dcspy-app')
        self.status_txt.set(f'You can close GUI')
        t.start()

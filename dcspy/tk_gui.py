import tkinter as tk
from logging import getLogger

LOG = getLogger(__name__)


class DcspyGui(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        """
        Basic constructor.

        :param master: Top level widget
        """
        super().__init__(master)
        self.master = master
        self.pack()
        self.lcd_type = tk.StringVar()
        self._init_widgets()

    def _init_widgets(self) -> None:
        frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        lcd_types = {'G19': 'G19', 'G510': 'G510', 'G15 v1/v2': 'G15', 'G13': 'G13'}
        for text, value in lcd_types.items():
            rb = tk.Radiobutton(master=frame, text=text, variable=self.lcd_type, value=value, command=self._lcd_type_selected)
            rb.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
            rb.select()

        start = tk.Button(master=self.master, text='Start', command=DcspyGui.start_dcspy)
        close = tk.Button(master=self.master, text='Close', command=self.master.destroy)

        frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        start.pack(side=tk.TOP, fill=tk.X, expand=True)
        close.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    def _lcd_type_selected(self) -> None:
        """Handling selected LCD type."""
        LOG.info(f'Logitech {self.lcd_type} selected')

    @staticmethod
    def start_dcspy() -> None:
        """Run real application."""
        from dcspy import starter
        starter.run()

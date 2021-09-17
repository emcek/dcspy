import tkinter as tk
from logging import getLogger
from threading import Thread

from dcspy import LCD_TYPES, save_cfg, config
from dcspy.starter import dcspy_run

LOG = getLogger(__name__)


class DcspyGui(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        """
        Create basic GUI for dcspy application.

        :param master: Top level widget
        """
        super().__init__(master)
        self.master = master
        self.master.title('GUI')
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
        for i, text in enumerate(LCD_TYPES):
            rb_lcd_type = tk.Radiobutton(master=frame, text=text, variable=self.lcd_type, value=text, command=self._lcd_type_selected)
            rb_lcd_type.grid(row=i, column=0, pady=0, padx=2, sticky=tk.W)
            if config.get('keyboard', 'G13') == text:
                rb_lcd_type.select()

        start = tk.Button(master=self.master, text='Start', command=self.start_dcspy)
        close = tk.Button(master=self.master, text='Close', command=self.master.destroy)
        status = tk.Label(master=self.master, textvariable=self.status_txt)

        frame.grid(row=0, column=0, padx=2, pady=2, rowspan=2)
        start.grid(row=0, column=1, padx=2, pady=2)
        close.grid(row=1, column=1, padx=2, pady=2)
        status.grid(row=2, column=0, columnspan=2, sticky=tk.W)

    def _lcd_type_selected(self) -> None:
        """Handling selected LCD type."""
        keyboard = self.lcd_type.get()
        LOG.debug(f'Logitech {keyboard} selected')
        self.status_txt.set(f'Logitech {keyboard} selected')
        save_cfg(cfg_dict={'keyboard': keyboard})

    def start_dcspy(self) -> None:
        """Run real application."""
        keyboard = self.lcd_type.get()
        save_cfg(cfg_dict={'keyboard': keyboard})
        app_params = {'lcd_type': LCD_TYPES[keyboard]}
        app_thread = Thread(target=dcspy_run, kwargs=app_params)
        LOG.debug(f'Starting thread for: {app_params}')
        app_thread.setName('dcspy-app')
        self.status_txt.set('You can close GUI')
        app_thread.start()

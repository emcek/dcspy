import tkinter as tk
from logging import getLogger
from sys import prefix
from threading import Thread

from dcspy import LCD_TYPES, config
from dcspy.starter import dcspy_run
from dcspy.utils import save_cfg

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
        self.cfg_status = tk.StringVar()
        self._init_widgets()

    def _init_widgets(self) -> None:
        self.master.columnconfigure(index=0, weight=1)
        self.master.columnconfigure(index=1, weight=1)
        self.master.rowconfigure(index=0, weight=1)
        self.master.rowconfigure(index=1, weight=1)
        self.master.rowconfigure(index=2, weight=1)
        self.master.rowconfigure(index=3, weight=1)

        frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        for i, text in enumerate(LCD_TYPES):
            rb_lcd_type = tk.Radiobutton(master=frame, text=text, variable=self.lcd_type, value=text, command=self._lcd_type_selected)
            rb_lcd_type.grid(row=i, column=0, pady=0, padx=2, sticky=tk.W)
            if config.get('keyboard', 'G13') == text:
                rb_lcd_type.select()

        start = tk.Button(master=self.master, text='Start', width=6, command=self.start_dcspy)
        cfg = tk.Button(master=self.master, text='Config', width=6, command=self._cfg_window)
        close = tk.Button(master=self.master, text='Close', width=6, command=self.master.destroy)
        status = tk.Label(master=self.master, textvariable=self.status_txt)

        frame.grid(row=0, column=0, padx=2, pady=2, rowspan=3)
        start.grid(row=0, column=1, padx=2, pady=2)
        cfg.grid(row=1, column=1, padx=2, pady=2)
        close.grid(row=2, column=1, padx=2, pady=2)
        status.grid(row=3, column=0, columnspan=2, sticky=tk.W)

    def _lcd_type_selected(self) -> None:
        """Handling selected LCD type."""
        keyboard = self.lcd_type.get()
        LOG.debug(f'Logitech {keyboard} selected')
        self.status_txt.set(f'Logitech {keyboard} selected')
        save_cfg(cfg_dict={'keyboard': keyboard})

    def _cfg_window(self):
        cfg_edit = tk.Toplevel(self.master)
        cfg_edit.title('Config Editor')
        width, height = 450, 200
        cfg_edit.geometry(f'{width}x{height}')
        cfg_edit.minsize(width=250, height=150)
        cfg_edit.iconbitmap(f'{prefix}/dcspy_data/dcspy.ico')

        scrollbar_y = tk.Scrollbar(cfg_edit, orient='vertical')
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        # from tkinter import font
        # print(font.families())
        # print(font.names())
        text_info = tk.Text(master=cfg_edit, width=10, height=5, yscrollcommand=scrollbar_y.set, wrap=tk.WORD,
                            font=('Courier New', 10), selectbackground='purple', selectforeground='white', undo=True)
        text_info.pack(fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=text_info.yview)
        load = tk.Button(master=cfg_edit, text='Load', width=6, command=self._load_cfg)
        save = tk.Button(master=cfg_edit, text='Save', width=6, command=self._save_cfg)
        quit = tk.Button(master=cfg_edit, text='Quit', width=6, command=cfg_edit.destroy)
        load.pack(side=tk.LEFT)
        save.pack(side=tk.LEFT)
        quit.pack(side=tk.LEFT)
        statusbar = tk.Label(master=cfg_edit, textvariable=self.cfg_status, anchor=tk.E)
        self.cfg_status.set('Ready')
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_cfg(self):
        pass

    def _save_cfg(self):
        pass

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

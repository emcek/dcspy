import tkinter as tk
from functools import partial
from logging import getLogger
from os import path, environ
from re import search
from shutil import unpack_archive, rmtree, copytree
from sys import prefix
from threading import Thread
from tkinter import messagebox
from typing import NamedTuple

from dcspy import LCD_TYPES, config
from dcspy.starter import dcspy_run
from dcspy.utils import save_cfg, load_cfg, check_ver_at_github, download_file, proc_is_running

LOG = getLogger(__name__)
BiosRelease = NamedTuple('BiosRelease', [('latest', bool), ('ver', str), ('dl_url', str),
                                         ('published', str), ('release_type', str), ('archive_file', str)])


class DcspyGui(tk.Frame):
    def __init__(self, master: tk.Tk, config_file: str) -> None:
        """
        Create basic GUI for dcspy application.

        :param master: Top level widget
        :param config_file: path to configuration yaml file
        """
        super().__init__(master)
        self.master = master
        self.master.title('GUI')
        self.lcd_type = tk.StringVar()
        self.status_txt = tk.StringVar()
        self.cfg_file = config_file
        self._init_widgets()
        self.l_bios = 'Not checked'
        self.r_bios = 'Not checked'
        self.bios_path = ''

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
        cfg = tk.Button(master=self.master, text='Config', width=6, command=self._config_editor)
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

    def _config_editor(self) -> None:
        """Config and settings editor window."""
        cfg_edit = tk.Toplevel(self.master)
        cfg_edit.title('Config Editor')
        width, height = 580, 200
        cfg_edit.geometry(f'{width}x{height}')
        cfg_edit.minsize(width=250, height=150)
        cfg_edit.iconbitmap(f'{prefix}/dcspy_data/dcspy.ico')

        editor_status = tk.Label(master=cfg_edit, text=f'Configuration file: {self.cfg_file}', anchor=tk.W)
        editor_status.pack(side=tk.TOP, fill=tk.X)
        scrollbar_y = tk.Scrollbar(cfg_edit, orient='vertical')
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        text_editor = tk.Text(master=cfg_edit, width=10, height=5, yscrollcommand=scrollbar_y.set, wrap=tk.CHAR, relief=tk.GROOVE,
                              borderwidth=2, font=('Courier New', 10), selectbackground='purple', selectforeground='white', undo=True)
        text_editor.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar_y.config(command=text_editor.yview)
        load = tk.Button(master=cfg_edit, text='Load', width=6, command=partial(self._load_cfg, text_editor))
        save = tk.Button(master=cfg_edit, text='Save', width=6, command=partial(self._save_cfg, text_editor))
        bios_status = tk.Label(master=cfg_edit, text=f'Local BIOS: {self.l_bios}  |  Remote BIOS: {self.r_bios}', anchor=tk.E)
        check_bios = tk.Button(master=cfg_edit, text='Check DCS-BIOS', width=14, command=partial(self._check_bios, bios_status))
        close = tk.Button(master=cfg_edit, text='Close', width=6, command=cfg_edit.destroy)
        load.pack(side=tk.LEFT)
        save.pack(side=tk.LEFT)
        check_bios.pack(side=tk.LEFT)
        close.pack(side=tk.LEFT)
        bios_status.pack(side=tk.BOTTOM, fill=tk.X)
        self._load_cfg(text_editor)

    def _load_cfg(self, text_widget: tk.Text) -> None:
        text_widget.delete('1.0', tk.END)
        with open(self.cfg_file, 'r') as cfg_file:
            text_widget.insert(tk.END, cfg_file.read().strip())

    def _save_cfg(self, text_info: tk.Text) -> None:
        with open(self.cfg_file, 'w+') as cfg_file:
            cfg_file.write(text_info.get('1.0', tk.END).strip())

    def _check_bios(self, bios_statusbar) -> None:
        check_local_bios = self._check_local_bios()
        check_remote_bios = self._check_remote_bios()
        bios_statusbar.config(text=f'Local BIOS: {self.l_bios}  |  Remote BIOS: {self.r_bios}')
        dcs_runs = proc_is_running(name='DCS.exe')

        if all([check_local_bios, check_remote_bios.ver, not dcs_runs]):
            self._ask_to_update(check_remote_bios)
        else:
            msg = self._get_problem_desc(check_local_bios, bool(check_remote_bios.ver), bool(dcs_runs))
            messagebox.showwarning('Update', msg)

    def _get_problem_desc(self, local_bios: bool, remote_bios: bool, dcs: bool) -> str:
        dcs_chk = '\u2716 DCS' if dcs else '\u2714 DCS'
        dcs_sta = 'running' if dcs else 'not running'
        dcs_note = ' - Quit is recommended.' if dcs else ''
        lbios_chk = '\u2714 Local' if local_bios else '\u2716 Local'
        lbios_note = '' if local_bios else ' - Check "dcsbios" path in config.'
        rbios_chk = '\u2714 Remote' if remote_bios else '\u2716 Remote'
        rbios_note = '' if remote_bios else ' - Check internet connection.'

        return f'{dcs_chk}: {dcs_sta}{dcs_note}\n' \
               f'{lbios_chk} Bios ver: {self.l_bios}{lbios_note}\n' \
               f'{rbios_chk} Bios ver: {self.r_bios}{rbios_note}'

    def _check_local_bios(self) -> bool:
        result = False
        bios_path = load_cfg()['dcsbios']
        self.l_bios = 'Unknown'
        try:
            with open(path.join(bios_path, 'Lib\\CommonData.lua')) as cd_lua:  # type: ignore
                cd_lua_data = cd_lua.read()
        except FileNotFoundError as err:
            LOG.debug(f'{err.__class__.__name__}: {err.filename}')
        else:
            self.bios_path = bios_path
            bios_re = search(r'function getVersion\(\)\s*return\s*\"([\d.]*)\"', cd_lua_data)
            if bios_re:
                self.l_bios = bios_re.group(1)
                result = True
        return result

    def _check_remote_bios(self) -> BiosRelease:
        latest, ver, dl_url, published, pre_release = check_ver_at_github(repo='DCSFlightpanels/dcs-bios',
                                                                          current_ver=self.l_bios)
        archive_file = dl_url.split('/')[-1]
        release_type = 'Pre-release' if pre_release else 'Regular'
        self.r_bios = ver if ver else 'Unknown'
        return BiosRelease(latest, ver, dl_url, published, release_type, archive_file)

    def _ask_to_update(self, results: BiosRelease) -> None:
        msg_txt = f'You are running latest {results.ver} version.\n' \
                  f'Type: {results.release_type}\n' \
                  f'Released: {results.published}\n\n' \
                  f'Would you like to download {results.archive_file} and overwrite update?'
        if not results.latest:
            msg_txt = f'You are running latest {self.l_bios} version.\n' \
                      f'New version {results.ver} available.\n' \
                      f'Type: {results.release_type}\n' \
                      f'Released: {results.published}\n\n' \
                      f'Would you like to update?'
        if messagebox.askokcancel('Update DCS-BIOS', msg_txt):
            self._update(results)

    def _update(self, results):
        tmp_dir = environ.get('TEMP', 'C:\\')
        local_zip = path.join(tmp_dir, results.archive_file)
        download_file(url=results.dl_url, save_path=local_zip)
        LOG.debug(f'Remove DCS-BIOS from: {tmp_dir} ')
        rmtree(path=path.join(tmp_dir, 'DCS-BIOS'), ignore_errors=True)
        LOG.debug(f'Unpack file: {local_zip} ')
        unpack_archive(filename=local_zip, extract_dir=tmp_dir)
        LOG.debug(f'Remove: {self.bios_path} ')
        rmtree(self.bios_path)
        LOG.debug(f'Copy DCS-BIOS to: {self.bios_path} ')
        copytree(src=path.join(tmp_dir, 'DCS-BIOS'), dst=self.bios_path)
        messagebox.showinfo('Updated', 'Success. Done.')

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

import tkinter as tk
from functools import partial
from logging import getLogger
from os import path
from re import search
from shutil import unpack_archive, rmtree, copy, copytree
from tempfile import gettempdir
from threading import Thread, Event
from tkinter import messagebox
from typing import NamedTuple, Union
from webbrowser import open_new

from packaging import version

from dcspy import LCD_TYPES, config
from dcspy.starter import dcspy_run
from dcspy.utils import save_cfg, load_cfg, check_ver_at_github, download_file, proc_is_running

__version__ = '1.7.5'
LOG = getLogger(__name__)


class ReleaseInfo(NamedTuple):
    """Tuple to store release related information."""
    latest: bool
    ver: Union[version.Version, version.LegacyVersion]
    dl_url: str
    published: str
    release_type: str
    archive_file: str


class DcspyGui(tk.Frame):
    """Tkinter GUI."""
    def __init__(self, master: tk.Tk, config_file: str) -> None:
        """
        Create basic GUI for dcspy application.

        :param master: Top level widget
        :param config_file: path to configuration yaml file
        """
        super().__init__(master)
        self.master = master
        self.master.title('DCSpy')
        self.lcd_type = tk.StringVar()
        self.status_txt = tk.StringVar()
        self.cfg_file = config_file
        self._init_widgets()
        self.l_bios: Union[version.Version, version.LegacyVersion] = version.LegacyVersion('Not checked')
        self.r_bios: Union[version.Version, version.LegacyVersion] = version.LegacyVersion('Not checked')
        self.bios_path = ''
        self.event = Event()
        self.status_txt.set(f'ver. {__version__}')
        self.btn_start.config(state=tk.ACTIVE)
        self.btn_stop.config(state=tk.DISABLED)
        if config.get('autostart', False):
            self.start_dcspy()

    def _init_widgets(self) -> None:
        """Init all GUI widgest."""
        self.master.columnconfigure(index=0, weight=1)
        self.master.columnconfigure(index=1, weight=1)
        self.master.rowconfigure(index=0, weight=1)
        self.master.rowconfigure(index=1, weight=1)
        self.master.rowconfigure(index=2, weight=1)
        self.master.rowconfigure(index=3, weight=1)

        frame = tk.Frame(master=self.master, relief=tk.GROOVE, borderwidth=2)
        frame.grid(row=0, column=0, padx=2, pady=2, rowspan=3)
        for i, text in enumerate(LCD_TYPES):
            rb_lcd_type = tk.Radiobutton(master=frame, text=text, variable=self.lcd_type, value=text, command=self._lcd_type_selected)
            rb_lcd_type.grid(row=i, column=0, pady=0, padx=2, sticky=tk.W)
            if config.get('keyboard', 'G13') == text:
                rb_lcd_type.select()

        self._add_buttons_mainwindow()

    def _add_buttons_mainwindow(self):
        """Add buttons to GUI."""
        self.btn_start = tk.Button(master=self.master, text='Start', width=6, command=self.start_dcspy)
        cfg = tk.Button(master=self.master, text='Config', width=6, command=self._config_editor)
        self.btn_stop = tk.Button(master=self.master, text='Stop', width=6, state=tk.DISABLED, command=self._stop)
        close = tk.Button(master=self.master, text='Close', width=6, command=self.master.destroy)
        status = tk.Label(master=self.master, textvariable=self.status_txt)
        self.btn_start.grid(row=0, column=1, padx=2, pady=2)
        cfg.grid(row=1, column=1, padx=2, pady=2)
        self.btn_stop.grid(row=2, column=1, padx=2, pady=2)
        close.grid(row=3, column=1, padx=2, pady=2)
        status.grid(row=4, column=0, columnspan=2, sticky=tk.W)

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
        width, height = 580, 270
        cfg_edit.geometry(f'{width}x{height}')
        cfg_edit.minsize(width=250, height=150)

        editor_status = tk.Label(master=cfg_edit, text=f'Configuration file: {self.cfg_file}', anchor=tk.W)
        editor_status.pack(side=tk.TOP, fill=tk.X)
        scrollbar_y = tk.Scrollbar(cfg_edit, orient='vertical')
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        text_editor = self._create_text_editor(cfg_edit, scrollbar_y)
        self._load_cfg(text_editor)

    def _create_text_editor(self, cfg_edit, scrollbar_y):
        """
        Create settings editor.

        :param cfg_edit: aster widget
        :param scrollbar_y: scrollbar
        :return: editor widget
        """
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
        return text_editor

    def _load_cfg(self, text_widget: tk.Text) -> None:
        """
        Load configuration into settings editor.

        :param text_widget: text widget
        """
        text_widget.delete('1.0', tk.END)
        with open(file=self.cfg_file, encoding='utf-8') as cfg_file:
            text_widget.insert(tk.END, cfg_file.read().strip())

    def _save_cfg(self, text_info: tk.Text) -> None:
        """
        Save configuration from settings editor.

        :param text_info: text widget
        """
        with open(file=self.cfg_file, mode='w+', encoding='utf-8') as cfg_file:
            cfg_file.write(text_info.get('1.0', tk.END).strip())

    def _check_bios(self, bios_statusbar) -> None:
        """
        Check version and configuration of DCS-BIOS.

        :param bios_statusbar: statusbar
        """
        self._check_local_bios()
        remote_bios_info = self._check_remote_bios()
        bios_statusbar.config(text=f'Local BIOS: {self.l_bios}  |  Remote BIOS: {self.r_bios}')
        correct_local_bios_ver = isinstance(self.l_bios, version.Version)
        correct_remote_bios_ver = isinstance(self.r_bios, version.Version)
        dcs_runs = proc_is_running(name='DCS.exe')

        if all([correct_remote_bios_ver, not dcs_runs]):
            self._ask_to_update(rel_info=remote_bios_info)
        else:
            msg = self._get_problem_desc(correct_local_bios_ver, correct_remote_bios_ver, bool(dcs_runs))
            messagebox.showwarning('Update', msg)

    def _get_problem_desc(self, local_bios: bool, remote_bios: bool, dcs: bool) -> str:
        """
        Describe issues with DCS-BIOS update.

        :param local_bios: local BIOS version
        :param remote_bios: remote BIOS version
        :param dcs: DCS is running
        :return: description as string
        """
        dcs_chk = '\u2716 DCS' if dcs else '\u2714 DCS'
        dcs_sta = 'running' if dcs else 'not running'
        dcs_note = '\n     Quit is recommended.' if dcs else ''
        lbios_chk = '\u2714 Local' if local_bios else '\u2716 Local'
        lbios_note = '' if local_bios else '\n     Check "dcsbios" path in config'
        rbios_chk = '\u2714 Remote' if remote_bios else '\u2716 Remote'
        rbios_note = '' if remote_bios else '\n     Check internet connection.'

        return f'{dcs_chk}: {dcs_sta}{dcs_note}\n' \
               f'{lbios_chk} Bios ver: {self.l_bios}{lbios_note}\n' \
               f'{rbios_chk} Bios ver: {self.r_bios}{rbios_note}'

    def _check_local_bios(self) -> ReleaseInfo:
        """
        Check version of local BIOS.

        :return: release description info
        """
        self.bios_path = load_cfg()['dcsbios']  # type: ignore
        self.l_bios = version.parse('not installed')
        result = ReleaseInfo(False, self.l_bios, '', '', '', '')
        try:
            with open(file=path.join(self.bios_path, 'lib\\CommonData.lua'), encoding='utf-8') as cd_lua:  # type: ignore
                cd_lua_data = cd_lua.read()
        except FileNotFoundError as err:
            LOG.debug(f'{err.__class__.__name__}: {err.filename}')
        else:
            bios_re = search(r'function getVersion\(\)\s*return\s*\"([\d.]*)\"', cd_lua_data)
            if bios_re:
                self.l_bios = version.parse(bios_re.group(1))
                result = ReleaseInfo(False, self.l_bios, '', '', '', '')
        return result

    def _check_remote_bios(self) -> ReleaseInfo:
        """
        Check version of remote BIOS.

        :return: release description info
        """
        release_info = check_ver_at_github(repo='DCSFlightpanels/dcs-bios', current_ver=str(self.l_bios))
        self.r_bios = release_info[1]
        return ReleaseInfo(*release_info)

    def _ask_to_update(self, rel_info: ReleaseInfo) -> None:
        """
        Ask user if update BIOS or not.

        :param rel_info: remote release information
        """
        msg_txt = f'You are running latest {rel_info.ver} version.\n' \
                  f'Type: {rel_info.release_type}\n' \
                  f'Released: {rel_info.published}\n\n' \
                  f'Would you like to download {rel_info.archive_file} and overwrite update?'
        if not rel_info.latest:
            msg_txt = f'You are running {self.l_bios} version.\n' \
                      f'New version {rel_info.ver} available.\n' \
                      f'Type: {rel_info.release_type}\n' \
                      f'Released: {rel_info.published}\n\n' \
                      f'Would you like to update?'
        if messagebox.askokcancel('Update DCS-BIOS', msg_txt):
            self._update(rel_info=rel_info)

    def _update(self, rel_info: ReleaseInfo) -> None:
        """
        Perform BIOS update and check configuration.

        :param rel_info: remote release information
        """
        tmp_dir = gettempdir()
        local_zip = path.join(tmp_dir, rel_info.archive_file)
        download_file(url=rel_info.dl_url, save_path=local_zip)
        LOG.debug(f'Remove DCS-BIOS from: {tmp_dir} ')
        rmtree(path=path.join(tmp_dir, 'DCS-BIOS'), ignore_errors=True)
        LOG.debug(f'Unpack file: {local_zip} ')
        unpack_archive(filename=local_zip, extract_dir=tmp_dir)
        LOG.debug(f'Remove: {self.bios_path} ')
        rmtree(path=self.bios_path, ignore_errors=True)
        LOG.debug(f'Copy DCS-BIOS to: {self.bios_path} ')
        copytree(src=path.join(tmp_dir, 'DCS-BIOS'), dst=self.bios_path)
        install_result = self._handling_export_lua(tmp_dir)
        if 'github' in install_result:
            if messagebox.askyesno('Open browser', install_result):
                open_new(r'https://github.com/DCSFlightpanels/DCSFlightpanels/wiki/Installation')
        else:
            messagebox.showinfo('Updated', install_result)

    def _handling_export_lua(self, temp_dir: str) -> str:
        """
        Check if Export.lua file exist and its content.

        If not copy Export.lua from DCS-BIOS installation archive.

        :param temp_dir: directory with DCS-BIOS archive
        :return: result of checks
        """
        result = 'Installation Success. Done.'
        lua_dst_path = path.join(self.bios_path, '..')
        lua = 'Export.lua'
        try:
            with open(file=path.join(lua_dst_path, lua), encoding='utf-8') as lua_dst:  # type: ignore
                lua_dst_data = lua_dst.read()
        except FileNotFoundError as err:
            LOG.debug(f'{err.__class__.__name__}: {err.filename}')
            copy(src=path.join(temp_dir, lua), dst=lua_dst_path)
            LOG.debug(f'Copy Export.lua from: {temp_dir} to {lua_dst_path} ')
        else:
            result += self._check_dcs_bios_entry(lua_dst_data, lua_dst_path, temp_dir)
        return result

    @staticmethod
    def _check_dcs_bios_entry(lua_dst_data: str, lua_dst_path: str, temp_dir: str) -> str:
        """
        Check DCS-BIOS entry in Export.lua file.

        :param lua_dst_data: content of Export.lua
        :param lua_dst_path: Export.lua path
        :param temp_dir: directory with DCS-BIOS archive
        :return: result of checks
        """
        result = '\n\nExport.lua exists.'
        lua = 'Export.lua'
        with open(file=path.join(temp_dir, lua), encoding='utf-8') as lua_src:  # type: ignore
            lua_src_data = lua_src.read()
        export_re = search(r'dofile\(lfs.writedir\(\)\.\.\[\[Scripts\\DCS-BIOS\\BIOS\.lua\]\]\)', lua_dst_data)
        if not export_re:
            with open(file=path.join(lua_dst_path, lua), mode='a+',
                      encoding='utf-8') as exportlua_dst:  # type: ignore
                exportlua_dst.write(f'\n{lua_src_data}')
            LOG.debug(f'Add DCS-BIOS to Export.lua: {lua_src_data}')
            result += '\n\nDCS-BIOS entry added.\n\nYou verify installation at:\ngithub.com/DCSFlightpanels/DCSFlightpanels/wiki/Installation'
        else:
            result += '\n\nDCS-BIOS entry detected.'
        return result

    def _stop(self) -> None:
        """Set event to stop DCSpy."""
        self.status_txt.set('Start again or close DCSpy')
        self.btn_start.config(state=tk.ACTIVE)
        self.btn_stop.config(state=tk.DISABLED)
        self.event.set()

    def start_dcspy(self) -> None:
        """Run real application."""
        self.event = Event()
        LOG.debug(f'Local DCS-BIOS version: {self._check_local_bios().ver}')
        keyboard = self.lcd_type.get()
        save_cfg(cfg_dict={'keyboard': keyboard})
        app_params = {'lcd_type': LCD_TYPES[keyboard], 'event': self.event}
        app_thread = Thread(target=dcspy_run, kwargs=app_params)
        app_thread.name = 'dcspy-app'
        LOG.debug(f'Starting thread {app_thread} for: {app_params}')
        self.status_txt.set('You can close GUI')
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.ACTIVE)
        app_thread.start()

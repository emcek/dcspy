import tkinter as tk
from functools import partial
from logging import getLogger
from os import path
from re import search
from shutil import unpack_archive, rmtree, copy, copytree
from tempfile import gettempdir
from threading import Thread, Event
from tkinter import messagebox
from typing import Union
from webbrowser import open_new

import customtkinter
from PIL import Image
from packaging import version

from dcspy import LCD_TYPES, config
from dcspy.starter import dcspy_run
from dcspy.utils import save_cfg, check_ver_at_github, download_file, proc_is_running, defaults_cfg, ReleaseInfo

__version__ = '1.7.5'
LOG = getLogger(__name__)


class DcspyGui(tk.Frame):
    """Tkinter GUI."""
    def __init__(self, master: customtkinter.CTk, config_file: str) -> None:
        """
        Create basic GUI for dcspy application.

        :param master: Top level widget
        :param config_file: path to configuration yaml file
        """
        super().__init__(master)
        self.master = master
        self.cfg_file = config_file
        self.l_bios: Union[version.Version, version.LegacyVersion] = version.LegacyVersion('Not checked')
        self.r_bios: Union[version.Version, version.LegacyVersion] = version.LegacyVersion('Not checked')
        self.event = Event()

        self.status_txt = tk.StringVar()
        result = check_ver_at_github(repo='emcek/dcspy', current_ver=__version__)
        current_ver = 'latest' if result.latest else 'please update!'
        self.status_txt.set(f'ver. {__version__} ({current_ver})')
        self.lcd_type = tk.StringVar()
        self.bios_path = tk.StringVar()
        self.dcs_path = tk.StringVar()
        self.autostart_switch = customtkinter.BooleanVar()
        self.showgui_switch = customtkinter.BooleanVar()
        self.verbose_switch = customtkinter.BooleanVar()
        self.mono_l = tk.StringVar()
        self.mono_s = tk.StringVar()
        self.mono_xs = tk.StringVar()
        self.color_l = tk.StringVar()
        self.color_s = tk.StringVar()
        self.color_xs = tk.StringVar()
        self.size_mono_l = tk.IntVar()
        self.size_mono_s = tk.IntVar()
        self.size_mono_xs = tk.IntVar()
        self.size_color_l = tk.IntVar()
        self.size_color_s = tk.IntVar()
        self.size_color_xs = tk.IntVar()
        self.font_name = tk.StringVar()
        self.theme_color = tk.StringVar()
        self.theme_mode = tk.StringVar()

        self._init_widgets()
        self._load_cfg()
        if config.get('autostart', False):
            self.start_dcspy()

    def _init_widgets(self) -> None:
        """Init all GUI widgets."""
        self.master.grid_columnconfigure(index=0, weight=0)
        self.master.grid_columnconfigure(index=1, weight=1)
        self.master.grid_rowconfigure(index=0, weight=1)
        self.master.grid_rowconfigure(index=1, weight=1)
        self.master.grid_rowconfigure(index=2, weight=1)
        self._sidebar()
        tabview = customtkinter.CTkTabview(master=self.master, width=250, height=400, state=tk.ACTIVE)
        tabview.grid(column=1, row=1, padx=30, pady=30, sticky=tk.N + tk.E + tk.S + tk.W)
        tabview.add('Keyboards')
        tabview.add('General')
        tabview.add('Mono')
        tabview.add('Color')
        self._keyboards(tabview)
        self._general_settings(tabview)
        self._mono_settings(tabview)
        self._color_settings(tabview)
        status = customtkinter.CTkLabel(master=self.master, textvariable=self.status_txt)
        status.grid(row=4, column=0, columnspan=2, sticky=tk.SE, padx=7)
        self.btn_start.configure(state=tk.ACTIVE)
        self.btn_stop.configure(state=tk.DISABLED)

    def _sidebar(self) -> None:
        """Configure sidebar of GUI."""
        sidebar_frame = customtkinter.CTkFrame(master=self.master, width=70, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, rowspan=4, sticky=tk.N + tk.S + tk.W)
        sidebar_frame.grid_rowconfigure(4, weight=1)
        logo_label = customtkinter.CTkLabel(master=sidebar_frame, text='Settings', font=customtkinter.CTkFont(size=20, weight='bold'))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        # load = customtkinter.CTkButton(master=sidebar_frame, text='Load', command=self._load_cfg)
        # load.grid(row=1, column=0, padx=20, pady=10)
        save = customtkinter.CTkButton(master=sidebar_frame, text='Save', command=self._save_cfg)
        save.grid(row=1, column=0, padx=20, pady=10)
        reset = customtkinter.CTkButton(master=sidebar_frame, text='Reset defaults', command=self._set_defaults_cfg)
        reset.grid(row=2, column=0, padx=20, pady=10)
        check_bios = customtkinter.CTkButton(master=sidebar_frame, text='Check DCS-BIOS', command=self._check_bios)
        check_bios.grid(row=3, column=0, padx=20, pady=10)
        self.btn_start = customtkinter.CTkButton(master=sidebar_frame, text='Start', command=self.start_dcspy)
        self.btn_start.grid(row=5, column=0, padx=20, pady=10)
        self.btn_stop = customtkinter.CTkButton(master=sidebar_frame, text='Stop', state=tk.DISABLED, command=self._stop)
        self.btn_stop.grid(row=6, column=0, padx=20, pady=10)
        close = customtkinter.CTkButton(master=sidebar_frame, text='Close', command=self.master.destroy)
        close.grid(row=7, column=0, padx=20, pady=10)

    def _keyboards(self, tabview: customtkinter.CTkTabview) -> None:
        """Configure keyboard tab GUI."""
        for i, text in enumerate(LCD_TYPES):
            icon = customtkinter.CTkImage(Image.open(path.join(path.abspath(path.dirname(__file__)), LCD_TYPES[text]['icon'])), size=(103, 70))
            label = customtkinter.CTkLabel(master=tabview.tab('Keyboards'), text='', image=icon)
            label.grid(row=i, column=0)
            rb_lcd_type = customtkinter.CTkRadioButton(master=tabview.tab('Keyboards'), text=text, variable=self.lcd_type, value=text, command=self._lcd_type_selected)
            rb_lcd_type.grid(row=i, column=1)
            if config.get('keyboard', 'G13') == text:
                rb_lcd_type.select()

    def _general_settings(self, tabview: customtkinter.CTkTabview) -> None:
        """Configure general tab GUI."""
        tabview.tab('General').grid_columnconfigure(index=0, weight=0)
        tabview.tab('General').grid_columnconfigure(index=1, weight=1)
        autostart_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='Autostart DCSpy:')
        autostart_label.grid(column=0, row=0, sticky=tk.W, pady=5)
        autostart = customtkinter.CTkSwitch(master=tabview.tab('General'), text='', variable=self.autostart_switch, onvalue=True, offvalue=False)
        autostart.grid(column=1, row=0, sticky=tk.W, padx=(10, 0), pady=5)
        showgui_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='Show GUI:')
        showgui_label.grid(column=0, row=1, sticky=tk.W, pady=5)
        showgui = customtkinter.CTkSwitch(master=tabview.tab('General'), text='', variable=self.showgui_switch, onvalue=True, offvalue=False)
        showgui.grid(column=1, row=1, sticky=tk.W, padx=(10, 0), pady=5)
        verbose_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='Show more logs:')
        verbose_label.grid(column=0, row=2, sticky=tk.W, pady=5)
        verbose = customtkinter.CTkSwitch(master=tabview.tab('General'), text='', variable=self.verbose_switch, onvalue=True, offvalue=False)
        verbose.grid(column=1, row=2, sticky=tk.W, padx=(10, 0), pady=5)
        dcs_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='DCS folder:')
        dcs_label.grid(column=0, row=3, sticky=tk.W, pady=5)
        dcs = customtkinter.CTkEntry(master=tabview.tab('General'), placeholder_text='DCS installation', width=390, textvariable=self.dcs_path)
        dcs.grid(column=1, row=3, sticky=tk.W + tk.E, padx=(10, 0), pady=5)
        bscbios_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='DCS-BIOS folder:')
        bscbios_label.grid(column=0, row=4, sticky=tk.W, pady=5)
        dcsbios = customtkinter.CTkEntry(master=tabview.tab('General'), placeholder_text='Path to DCS-BIOS', width=390, textvariable=self.bios_path)
        dcsbios.grid(column=1, row=4, sticky=tk.W + tk.E, padx=(10, 0), pady=5)
        appearance_mode_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='Appearance Mode:', anchor=tk.W)
        appearance_mode_label.grid(column=0, row=5, sticky=tk.W, pady=5)
        appearance_mode = customtkinter.CTkOptionMenu(master=tabview.tab('General'), values=['Light', 'Dark', 'System'], variable=self.theme_mode, command=self._change_mode)
        appearance_mode.grid(column=1, row=5, sticky=tk.W, padx=(10, 0), pady=5)
        color_theme_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='Color Theme:', anchor=tk.W)
        color_theme_label.grid(column=0, row=6, sticky=tk.W, pady=5)
        color_theme = customtkinter.CTkOptionMenu(master=tabview.tab('General'), values=['Blue', 'Green', 'Dark Blue'], variable=self.theme_color, command=self._change_color)
        color_theme.grid(column=1, row=6, sticky=tk.W, padx=(10, 0), pady=5)

    def _mono_settings(self, tabview: customtkinter.CTkTabview) -> None:
        """Configure mono tab GUI."""
        tabview.tab('Mono').grid_columnconfigure(index=0, weight=0)
        tabview.tab('Mono').grid_columnconfigure(index=1, weight=1)
        mono_l_label = customtkinter.CTkLabel(master=tabview.tab('Mono'), textvariable=self.mono_l)
        mono_l_label.grid(column=0, row=0, sticky=tk.W, padx=10, pady=5)
        mono_l = customtkinter.CTkSlider(master=tabview.tab('Mono'), from_=7, to=20, number_of_steps=13,
                                         command=partial(self._slider_event, 'mono_l'), variable=self.size_mono_l)
        mono_l.grid(column=1, row=0, sticky=tk.W + tk.E, padx=10, pady=5)
        mono_s_label = customtkinter.CTkLabel(master=tabview.tab('Mono'), textvariable=self.mono_s)
        mono_s_label.grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
        mono_s = customtkinter.CTkSlider(master=tabview.tab('Mono'), from_=7, to=20, number_of_steps=13,
                                         command=partial(self._slider_event, 'mono_s'), variable=self.size_mono_s)
        mono_s.grid(column=1, row=1, sticky=tk.W + tk.E, padx=10, pady=5)
        mono_xs_label = customtkinter.CTkLabel(master=tabview.tab('Mono'), textvariable=self.mono_xs)
        mono_xs_label.grid(column=0, row=2, sticky=tk.W, padx=10, pady=5)
        mono_xs = customtkinter.CTkSlider(master=tabview.tab('Mono'), from_=7, to=20, number_of_steps=13,
                                          command=partial(self._slider_event, 'mono_xs'), variable=self.size_mono_xs)
        mono_xs.grid(column=1, row=2, sticky=tk.W + tk.E, padx=10, pady=5)
        font_label = customtkinter.CTkLabel(master=tabview.tab('Mono'), text='Font name:')
        font_label.grid(column=0, row=3, sticky=tk.W, padx=10, pady=5)
        fontname = customtkinter.CTkEntry(master=tabview.tab('Mono'), placeholder_text='font name', textvariable=self.font_name)
        fontname.grid(column=1, row=3, sticky=tk.W + tk.E, padx=10, pady=5)

    def _color_settings(self, tabview: customtkinter.CTkTabview) -> None:
        """Configure color tab GUI."""
        tabview.tab('Color').grid_columnconfigure(index=0, weight=0)
        tabview.tab('Color').grid_columnconfigure(index=1, weight=1)
        color_l_label = customtkinter.CTkLabel(master=tabview.tab('Color'), textvariable=self.color_l)
        color_l_label.grid(column=0, row=0, sticky=tk.W, padx=10, pady=5)
        color_l = customtkinter.CTkSlider(master=tabview.tab('Color'), from_=15, to=40, number_of_steps=25, command=partial(self._slider_event, 'color_l'),
                                          variable=self.size_color_l)
        color_l.grid(column=1, row=0, sticky=tk.W + tk.E, padx=10, pady=5)
        color_s_label = customtkinter.CTkLabel(master=tabview.tab('Color'), textvariable=self.color_s)
        color_s_label.grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
        color_s = customtkinter.CTkSlider(master=tabview.tab('Color'), from_=15, to=40, number_of_steps=25, command=partial(self._slider_event, 'color_s'),
                                          variable=self.size_color_s)
        color_s.grid(column=1, row=1, sticky=tk.W + tk.E, padx=10, pady=5)
        color_xs_label = customtkinter.CTkLabel(master=tabview.tab('Color'), textvariable=self.color_xs)
        color_xs_label.grid(column=0, row=2, sticky=tk.W, padx=10, pady=5)
        color_xs = customtkinter.CTkSlider(master=tabview.tab('Color'), from_=15, to=40, number_of_steps=25,
                                           command=partial(self._slider_event, 'color_xs'), variable=self.size_color_xs)
        color_xs.grid(column=1, row=2, sticky=tk.W + tk.E, padx=10, pady=5)
        font_label = customtkinter.CTkLabel(master=tabview.tab('Color'), text='Font name:')
        font_label.grid(column=0, row=3, sticky=tk.W, padx=10, pady=5)
        fontname = customtkinter.CTkEntry(master=tabview.tab('Color'), placeholder_text='font name', width=150, textvariable=self.font_name)
        fontname.grid(column=1, row=3, sticky=tk.W + tk.E, padx=10, pady=5)

    def _slider_event(self, label: str, value: float):
        """
        Update correct label when slider is moved.

        :param label:
        :param value:
        """
        getattr(self, label).set(f'Font {" ".join([word.capitalize() for word in label.split("_")])} : {int(value)}')

    def _load_cfg(self) -> None:
        """Load configuration into GUI."""
        self.autostart_switch.set(config['autostart'])
        self.showgui_switch.set(config['show_gui'])
        self.verbose_switch.set(config['verbose'])
        self.dcs_path.set(str(config['dcs']))
        self.bios_path.set(str(config['dcsbios']))
        self.mono_l.set(f'Font Mono L : {config["font_mono_l"]}')
        self.mono_s.set(f'Font Mono S : {config["font_mono_s"]}')
        self.mono_xs.set(f'Font Mono Xs : {config["font_mono_xs"]}')
        self.color_l.set(f'Font Color L : {config["font_color_l"]}')
        self.color_s.set(f'Font Color S : {config["font_color_s"]}')
        self.color_xs.set(f'Font Color Xs : {config["font_color_xs"]}')
        self.size_mono_l.set(int(config["font_mono_l"]))
        self.size_mono_s.set(int(config["font_mono_s"]))
        self.size_mono_xs.set(int(config["font_mono_xs"]))
        self.size_color_l.set(int(config["font_color_l"]))
        self.size_color_s.set(int(config["font_color_s"]))
        self.size_color_xs.set(int(config["font_color_xs"]))
        self.font_name.set(str(config['font_name']))
        self.theme_mode.set(str(config['theme_mode']).capitalize())
        self.theme_color.set(str(config['theme_color']).replace('-', ' ').title())

    def _save_cfg(self) -> None:
        """Save configuration from GUI."""
        cfg = {
            'autostart': self.autostart_switch.get(),
            'show_gui': self.showgui_switch.get(),
            'verbose': self.verbose_switch.get(),
            'dcs': self.dcs_path.get(),
            'dcsbios': self.bios_path.get(),
            'font_mono_l': self.size_mono_l.get(),
            'font_mono_s': self.size_mono_s.get(),
            'font_mono_xs': self.size_mono_xs.get(),
            'font_color_l': self.size_color_l.get(),
            'font_color_s': self.size_color_s.get(),
            'font_color_xs': self.size_color_xs.get(),
            'font_name': self.font_name.get(),
            'theme_mode': self.theme_mode.get().lower(),
            'theme_color': self.theme_color.get().lower().replace(' ', '-'),
        }
        save_cfg(cfg_dict=cfg, filename=self.cfg_file)
        self.status_txt.set(f'Saved: {self.cfg_file}')

    def _set_defaults_cfg(self) -> None:
        """Set defaults and stop application."""
        save_cfg(cfg_dict=defaults_cfg, filename=self.cfg_file)
        messagebox.showwarning('Restart', 'DCSpy needs to be close.\nPlease start again manually!')
        self.master.destroy()

    def _lcd_type_selected(self) -> None:
        """Handling selected LCD type."""
        keyboard = self.lcd_type.get()
        LOG.debug(f'Logitech {keyboard} selected')
        self.status_txt.set(f'Logitech {keyboard} selected')
        save_cfg(cfg_dict={'keyboard': keyboard})

    @staticmethod
    def _change_mode(theme_mode: str) -> None:
        """
        Change theme mode.

        :param theme_mode: "System" (standard), "Dark", "Light"
        """
        save_cfg(cfg_dict={'theme_mode': theme_mode.lower()})
        customtkinter.set_appearance_mode(theme_mode)

    def _change_color(self, theme_color: str) -> None:
        """
        Save color theme and show message box to restart DCSpy.

        :param theme_color: value of color theme
        """
        save_cfg(cfg_dict={'theme_color': theme_color.lower().replace(' ', '-')})
        if messagebox.askokcancel('Change theme color', 'DCSpy needs to be close.\nIn order to apply color changes.\n\nPlease start again manually!'):
            self.master.destroy()

    def _check_bios(self) -> None:
        """Check version and configuration of DCS-BIOS."""
        self._check_local_bios()
        remote_bios_info = self._check_remote_bios()
        self.status_txt.set(f'Local BIOS: {self.l_bios} | Remote BIOS: {self.r_bios}')
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
        self.l_bios = version.parse('not installed')
        result = ReleaseInfo(False, self.l_bios, '', '', '', '')
        try:
            with open(file=path.join(self.bios_path.get(), 'lib\\CommonData.lua'), encoding='utf-8') as cd_lua:  # type: ignore
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
        self.r_bios = release_info.ver
        return release_info

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
        LOG.debug(f'Remove: {self.bios_path.get()} ')
        rmtree(path=self.bios_path.get(), ignore_errors=True)
        LOG.debug(f'Copy DCS-BIOS to: {self.bios_path.get()} ')
        copytree(src=path.join(tmp_dir, 'DCS-BIOS'), dst=self.bios_path.get())
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
        lua_dst_path = path.join(self.bios_path.get(), '..')
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
        self.btn_start.configure(state=tk.ACTIVE)
        self.btn_stop.configure(state=tk.DISABLED)
        self.event.set()

    def start_dcspy(self) -> None:
        """Run real application."""
        self.event = Event()
        LOG.debug(f'Local DCS-BIOS version: {self._check_local_bios().ver}')
        keyboard = self.lcd_type.get()
        save_cfg(cfg_dict={'keyboard': keyboard})
        app_params = {'lcd_type': LCD_TYPES[keyboard]['type'], 'event': self.event}
        app_thread = Thread(target=dcspy_run, kwargs=app_params)
        app_thread.name = 'dcspy-app'
        LOG.debug(f'Starting thread {app_thread} for: {app_params}')
        self.status_txt.set('You can close GUI')
        self.btn_start.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.ACTIVE)
        app_thread.start()

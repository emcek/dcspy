import tkinter as tk
from functools import partial
from logging import getLogger
from pathlib import Path
from platform import architecture, uname, python_implementation, python_version
from re import search
from shutil import unpack_archive, rmtree, copy, copytree
from tempfile import gettempdir
from threading import Thread, Event
from typing import Union
from webbrowser import open_new

import customtkinter
from CTkMessagebox import CTkMessagebox
from PIL import Image
from packaging import version

from dcspy import LCD_TYPES, config
from dcspy.starter import dcspy_run
from dcspy.utils import save_cfg, check_ver_at_github, download_file, proc_is_running, defaults_cfg, ReleaseInfo, get_version_string, check_dcs_ver, \
    check_github_repo, check_dcs_bios_entry

__version__ = '1.9.5'
LOG = getLogger(__name__)


class DcspyGui(tk.Frame):
    """Tkinter GUI."""
    def __init__(self, master: customtkinter.CTk) -> None:
        """
        Create basic GUI for dcspy application.

        :param master: Top level widget
        """
        super().__init__(master)
        self.master = master
        self.cfg_file = Path(__file__).resolve().with_name('config.yaml')
        self.l_bios: Union[version.Version, version.LegacyVersion] = version.LegacyVersion('Not checked')
        self.r_bios: Union[version.Version, version.LegacyVersion] = version.LegacyVersion('Not checked')
        self.event = Event()

        self.status_txt = tk.StringVar()
        self.lcd_type = tk.StringVar()
        self.bios_path = tk.StringVar()
        self.dcs_path = tk.StringVar()
        self.autostart_switch = customtkinter.BooleanVar()
        self.showgui_switch = customtkinter.BooleanVar()
        self.savelcd_switch = customtkinter.BooleanVar()
        self.checkver_switch = customtkinter.BooleanVar()
        self.verbose_switch = customtkinter.BooleanVar()
        self.dedfont_switch = customtkinter.BooleanVar()
        self.update_bios = customtkinter.BooleanVar()
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
        self.bios_git_switch = customtkinter.BooleanVar()
        self.bios_git_ref = tk.StringVar()

        self._load_cfg()
        self.btn_start: customtkinter.CTkButton
        self.btn_stop: customtkinter.CTkButton
        self.git_bios_switch: customtkinter.CTkSwitch
        self.bios_git_label: customtkinter.CTkLabel
        self.bios_git: customtkinter.CTkEntry
        self._init_widgets()
        self.status_txt.set(get_version_string(repo='emcek/dcspy', current_ver=__version__, check=config['check_ver']))
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
        tabview.add('Special')
        tabview.add('Advanced')
        tabview.add('About')
        self._keyboards(tabview)
        self._general_settings(tabview)
        self._mono_settings(tabview)
        self._color_settings(tabview)
        self._special_settings(tabview)
        self._advanced_settings(tabview)
        self._about(tabview)
        status = customtkinter.CTkLabel(master=self.master, textvariable=self.status_txt)
        status.grid(row=4, column=0, columnspan=2, sticky=tk.SE, padx=7)

    def _sidebar(self) -> None:
        """Configure sidebar of GUI."""
        sidebar_frame = customtkinter.CTkFrame(master=self.master, width=70, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, rowspan=4, sticky=tk.N + tk.S + tk.W)
        sidebar_frame.grid_rowconfigure(4, weight=1)
        logo_label = customtkinter.CTkLabel(master=sidebar_frame, text='Settings', font=customtkinter.CTkFont(size=20, weight='bold'))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        reset = customtkinter.CTkButton(master=sidebar_frame, text='Reset to defaults', command=self._set_defaults_cfg)
        reset.grid(row=1, column=0, padx=20, pady=10)
        check_bios = customtkinter.CTkButton(master=sidebar_frame, text='Update DCS-BIOS', command=self._update_bios)
        check_bios.grid(row=2, column=0, padx=20, pady=10)
        check_ver = customtkinter.CTkButton(master=sidebar_frame, text='Check DCSpy version', command=self._check_version)
        check_ver.grid(row=3, column=0, padx=20, pady=10)
        self.btn_start = customtkinter.CTkButton(master=sidebar_frame, text='Start', command=self.start_dcspy)
        logo_icon = customtkinter.CTkImage(Image.open(Path(__file__).resolve().with_name('dcspy.png')), size=(130, 60))
        logo_label = customtkinter.CTkLabel(master=sidebar_frame, text='', image=logo_icon)
        logo_label.grid(row=4, column=0, sticky=tk.W + tk.E)
        self.btn_start.grid(row=5, column=0, padx=20, pady=10)
        self.btn_stop = customtkinter.CTkButton(master=sidebar_frame, text='Stop', state=tk.DISABLED, command=self._stop)
        self.btn_stop.grid(row=6, column=0, padx=20, pady=10)
        close = customtkinter.CTkButton(master=sidebar_frame, text='Close', command=self.master.destroy)
        close.grid(row=7, column=0, padx=20, pady=10)
        self.btn_start.configure(state=tk.ACTIVE)
        self.btn_stop.configure(state=tk.DISABLED)

    def _keyboards(self, tabview: customtkinter.CTkTabview) -> None:
        """Configure keyboard tab GUI."""
        for i, text in enumerate(LCD_TYPES):
            icon = customtkinter.CTkImage(Image.open(Path(__file__).resolve().with_name(LCD_TYPES[text]['icon'])), size=(103, 70))
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
        autostart = customtkinter.CTkSwitch(master=tabview.tab('General'), text='', variable=self.autostart_switch, onvalue=True, offvalue=False, command=partial(self._save_cfg))
        autostart.grid(column=1, row=0, sticky=tk.W, padx=(10, 0), pady=5)
        showgui_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='Show GUI:')
        showgui_label.grid(column=0, row=1, sticky=tk.W, pady=5)
        showgui = customtkinter.CTkSwitch(master=tabview.tab('General'), text='', variable=self.showgui_switch, onvalue=True, offvalue=False, command=partial(self._save_cfg))
        showgui.grid(column=1, row=1, sticky=tk.W, padx=(10, 0), pady=5)
        checkver_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='Check version:')
        checkver_label.grid(column=0, row=2, sticky=tk.W, pady=5)
        checkver = customtkinter.CTkSwitch(master=tabview.tab('General'), text='', variable=self.checkver_switch, onvalue=True, offvalue=False, command=partial(self._save_cfg))
        checkver.grid(column=1, row=2, sticky=tk.W, padx=(10, 0), pady=5)
        dcs_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='DCS folder:')
        dcs_label.grid(column=0, row=3, sticky=tk.W, pady=5)
        dcs = customtkinter.CTkEntry(master=tabview.tab('General'), placeholder_text='DCS installation', width=390, textvariable=self.dcs_path,
                                     validate='key', validatecommand=(self.master.register(self._save_entry_text), '%P', '%W'))
        dcs.grid(column=1, row=3, sticky=tk.W + tk.E, padx=(10, 0), pady=5)
        bscbios_label = customtkinter.CTkLabel(master=tabview.tab('General'), text='DCS-BIOS folder:')
        bscbios_label.grid(column=0, row=4, sticky=tk.W, pady=5)
        dcsbios = customtkinter.CTkEntry(master=tabview.tab('General'), placeholder_text='Path to DCS-BIOS', width=390, textvariable=self.bios_path,
                                         validate='key', validatecommand=(self.master.register(self._save_entry_text), '%P', '%W'))
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
        fontname = customtkinter.CTkEntry(master=tabview.tab('Mono'), placeholder_text='font name', textvariable=self.font_name, validate='key',
                                          validatecommand=(self.master.register(self._save_entry_text), '%P', '%W'))
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
        fontname = customtkinter.CTkEntry(master=tabview.tab('Color'), placeholder_text='font name', width=150, textvariable=self.font_name, validate='key',
                                          validatecommand=(self.master.register(self._save_entry_text), '%P', '%W'))
        fontname.grid(column=1, row=3, sticky=tk.W + tk.E, padx=10, pady=5)

    def _special_settings(self, tabview: customtkinter.CTkTabview) -> None:
        """Configure special tab GUI."""
        tabview.tab('Special').grid_columnconfigure(index=0, weight=0)
        tabview.tab('Special').grid_columnconfigure(index=1, weight=1)
        dedfont_label = customtkinter.CTkLabel(master=tabview.tab('Special'), text='F-16 DED Font (only G19):')
        dedfont_label.grid(column=0, row=1, sticky=tk.W, pady=5)
        dedfont = customtkinter.CTkSwitch(master=tabview.tab('Special'), text='', variable=self.dedfont_switch, onvalue=True, offvalue=False, command=partial(self._save_cfg))
        dedfont.grid(column=1, row=1, sticky=tk.W, padx=(10, 0), pady=5)

    def _advanced_settings(self, tabview: customtkinter.CTkTabview) -> None:
        """Configure advanced tab GUI."""
        tabview.tab('Advanced').grid_columnconfigure(index=0, weight=0)
        tabview.tab('Advanced').grid_columnconfigure(index=1, weight=1)
        save_lcd_label = customtkinter.CTkLabel(master=tabview.tab('Advanced'), text='Save LCD screenshot:')
        save_lcd_label.grid(column=0, row=0, sticky=tk.W, pady=5)
        save_lcd = customtkinter.CTkSwitch(master=tabview.tab('Advanced'), text='', variable=self.savelcd_switch, onvalue=True, offvalue=False, command=partial(self._save_cfg))
        save_lcd.grid(column=1, row=0, sticky=tk.W, padx=(10, 0), pady=5)
        verbose_label = customtkinter.CTkLabel(master=tabview.tab('Advanced'), text='Show more logs:')
        verbose_label.grid(column=0, row=1, sticky=tk.W, pady=5)
        verbose = customtkinter.CTkSwitch(master=tabview.tab('Advanced'), text='', variable=self.verbose_switch, onvalue=True, offvalue=False, command=partial(self._save_cfg))
        verbose.grid(column=1, row=1, sticky=tk.W, padx=(10, 0), pady=5)
        update_bios_label = customtkinter.CTkLabel(master=tabview.tab('Advanced'), text='Auto Update DCS-BIOS:')
        update_bios_label.grid(column=0, row=2, sticky=tk.W, pady=5)
        update_bios = customtkinter.CTkSwitch(master=tabview.tab('Advanced'), text='', variable=self.update_bios, onvalue=True, offvalue=False, command=partial(self._save_cfg))
        update_bios.grid(column=1, row=2, sticky=tk.W, padx=(10, 0), pady=5)
        git_bios_label = customtkinter.CTkLabel(master=tabview.tab('Advanced'), text='Use live DCS-BIOS version:')
        git_bios_label.grid(column=0, row=3, sticky=tk.W, pady=5)
        self.git_bios_switch = customtkinter.CTkSwitch(master=tabview.tab('Advanced'), text='', variable=self.bios_git_switch, onvalue=True, offvalue=False, command=self._bios_git_switch)
        self.git_bios_switch.grid(column=1, row=3, sticky=tk.W, padx=(10, 0), pady=5)
        self.bios_git_label = customtkinter.CTkLabel(master=tabview.tab('Advanced'), state=tk.DISABLED, text='DCS-BIOS Git reference:', )
        self.bios_git = customtkinter.CTkEntry(master=tabview.tab('Advanced'), state=tk.DISABLED, placeholder_text='git reference', width=390, textvariable=self.bios_git_ref,
                                               validate='key', validatecommand=(self.master.register(self._save_entry_text), '%P', '%W'))
        if self.bios_git_switch.get():
            self.bios_git_label.configure(state=tk.ACTIVE)
            self.bios_git.configure(state=tk.NORMAL)

        self.bios_git_label.grid(column=0, row=4, sticky=tk.W, pady=5)
        self.bios_git.grid(column=1, row=4, sticky=tk.W + tk.E, padx=(10, 0), pady=5)

    def _about(self, tabview: customtkinter.CTkTabview) -> None:
        """About information."""
        system, _, release, ver, _, proc = uname()
        dcs_type, dcs_ver = check_dcs_ver(Path(config["dcs"]))
        self._auto_update_bios(silence=True)
        bios_ver = self._check_local_bios().ver
        sha_commit = f' SHA: {check_github_repo(git_ref="", update=False)}' if self.bios_git_switch.get() else ''
        dcs_bios_ver = f'{bios_ver}{sha_commit}'
        tabview.tab('About').grid_columnconfigure(index=0, weight=0)
        tabview.tab('About').grid_columnconfigure(index=1, weight=1)
        python1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='Python:')
        python1_label.grid(column=0, row=0, sticky=tk.W, padx=10, pady=5)
        python2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text=f'{python_implementation()}-{python_version()}')
        python2_label.grid(column=1, row=0, sticky=tk.W, padx=10, pady=5)
        system1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='System:')
        system1_label.grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
        system2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text=f'{system}{release} ver. {ver} ({architecture()[0]})')
        system2_label.grid(column=1, row=1, sticky=tk.W, padx=10, pady=5)
        processor1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='Processor:')
        processor1_label.grid(column=0, row=2, sticky=tk.W, padx=10, pady=5)
        processor2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text=f'{proc}')
        processor2_label.grid(column=1, row=2, sticky=tk.W, padx=10, pady=5)
        config1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='Config:')
        config1_label.grid(column=0, row=3, sticky=tk.W, padx=10, pady=5)
        config2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text=f'{self.cfg_file} (click to open)')
        config2_label.grid(column=1, row=3, sticky=tk.W, padx=10, pady=5)
        config2_label.bind('<Button-1>', lambda e: self._open_webpage(rf'file://{self.cfg_file}'))
        dcsp1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='DCSpy:')
        dcsp1_label.grid(column=0, row=4, sticky=tk.W, padx=10, pady=5)
        dcsp2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text=f'{__version__}')
        dcsp2_label.grid(column=1, row=4, sticky=tk.W, padx=10, pady=5)
        dcsbios1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='DCS-BIOS:')
        dcsbios1_label.grid(column=0, row=5, sticky=tk.W, padx=10, pady=5)
        dcsbios2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text=f'{dcs_bios_ver}')
        dcsbios2_label.grid(column=1, row=5, sticky=tk.W, padx=10, pady=5)
        dcsworld1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='DCS World:')
        dcsworld1_label.grid(column=0, row=6, sticky=tk.W, padx=10, pady=5)
        dcsworld2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text=f'{dcs_ver} {dcs_type} (click to open changelog)')
        dcsworld2_label.grid(column=1, row=6, sticky=tk.W, padx=10, pady=5)
        dcsworld2_label.bind('<Button-1>', lambda e: self._open_webpage('https://www.digitalcombatsimulator.com/en/news/changelog/openbeta/2.8.2.35759/'))
        homepage1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='Home page:')
        homepage1_label.grid(column=0, row=7, sticky=tk.W, padx=10, pady=5)
        homepage2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='https://github.com/emcek/dcspy (click to open)')
        homepage2_label.grid(column=1, row=7, sticky=tk.W, padx=10, pady=5)
        homepage2_label.bind('<Button-1>', lambda e: self._open_webpage('https://github.com/emcek/dcspy'))
        discord1_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='Discord:')
        discord1_label.grid(column=0, row=8, sticky=tk.W, padx=10, pady=5)
        discord2_label = customtkinter.CTkLabel(master=tabview.tab('About'), text='https://discord.gg/SP5Yjx3 (click to open)')
        discord2_label.grid(column=1, row=8, sticky=tk.W, padx=10, pady=5)
        discord2_label.bind('<Button-1>', lambda e: self._open_webpage('https://discord.gg/SP5Yjx3'))

    @staticmethod
    def _open_webpage(url: str) -> None:
        """
        Open default web browser URL page.

        :param url: URL address of web page
        """
        open_new(url)

    def _slider_event(self, label: str, value: float):
        """
        Update correct label when slider is moved.

        :param label:
        :param value:
        """
        getattr(self, label).set(f'Font {" ".join([word.capitalize() for word in label.split("_")])} : {int(value)}')
        self._save_cfg()

    def _bios_git_switch(self) -> None:
        """Change state of DSC-BIOS git version controls."""
        if self.git_bios_switch.get():
            self.bios_git_label.configure(state=tk.ACTIVE)
            self.bios_git.configure(state=tk.NORMAL)
        else:
            self.bios_git_label.configure(state=tk.DISABLED)
            self.bios_git.configure(state=tk.DISABLED)
        self._update_bios(silence=False)
        self._save_cfg()

    def _load_cfg(self) -> None:
        """Load configuration into GUI."""
        self.autostart_switch.set(config['autostart'])
        self.showgui_switch.set(config['show_gui'])
        self.savelcd_switch.set(config['save_lcd'])
        self.checkver_switch.set(config['check_ver'])
        self.verbose_switch.set(config['verbose'])
        self.dedfont_switch.set(config['f16_ded_font'])
        self.dcs_path.set(str(config['dcs']))
        self.bios_path.set(str(config['dcsbios']))
        self.bios_git_switch.set(config['git_bios'])
        self.update_bios.set(config['check_bios'])
        self.bios_git_ref.set(str(config['git_bios_ref']))
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
            'keyboard': self.lcd_type.get(),
            'autostart': self.autostart_switch.get(),
            'show_gui': self.showgui_switch.get(),
            'save_lcd': self.savelcd_switch.get(),
            'check_ver': self.checkver_switch.get(),
            'check_bios': self.update_bios.get(),
            'verbose': self.verbose_switch.get(),
            'f16_ded_font': self.dedfont_switch.get(),
            'dcs': self.dcs_path.get(),
            'dcsbios': self.bios_path.get(),
            'font_mono_l': self.size_mono_l.get(),
            'font_mono_s': self.size_mono_s.get(),
            'font_mono_xs': self.size_mono_xs.get(),
            'font_color_l': self.size_color_l.get(),
            'font_color_s': self.size_color_s.get(),
            'font_color_xs': self.size_color_xs.get(),
            'font_name': self.font_name.get(),
            'git_bios': self.bios_git_switch.get(),
            'git_bios_ref': self.bios_git_ref.get(),
            'theme_mode': self.theme_mode.get().lower(),
            'theme_color': self.theme_color.get().lower().replace(' ', '-'),
        }
        save_cfg(cfg_dict=cfg, filename=self.cfg_file)
        self.status_txt.set(f'Saved: {self.cfg_file}')

    def _set_defaults_cfg(self) -> None:
        """Set defaults and stop application."""
        save_cfg(cfg_dict=defaults_cfg, filename=self.cfg_file)
        CTkMessagebox(title='Restart', message='DCSpy needs to be close.\nPlease start again manually!', icon='warning', option_1='OK')
        self.master.destroy()

    def _lcd_type_selected(self) -> None:
        """Handling selected LCD type."""
        keyboard = self.lcd_type.get()
        LOG.debug(f'Logitech {keyboard} selected')
        self.status_txt.set(f'Logitech {keyboard} selected')
        self._save_cfg()

    def _change_mode(self, theme_mode: str) -> None:
        """
        Change theme mode.

        :param theme_mode: "System" (standard), "Dark", "Light"
        """
        customtkinter.set_appearance_mode(theme_mode)
        self._save_cfg()

    def _change_color(self, theme_color: str) -> None:
        """
        Save color theme and show message box to restart DCSpy.

        :param theme_color: value of color theme
        """
        msg = CTkMessagebox(title='Change theme color', message='DCSpy needs to be close.\nIn order to apply color changes.\n\nPlease start again manually!', icon='question', option_1='Yes', option_2='No')
        if msg.get() == 'Yes':
            self._save_cfg()
            LOG.debug(f'Select: {theme_color}')
            self.master.destroy()

    def _save_entry_text(self, what, widget) -> bool:
        """
        Hacking way to be able to trigger save method, when text of entry widget is changed.

        :param what: change text
        :param widget: widget name
        :return: always True
        """
        self._save_cfg()
        LOG.debug(f'Widget: {".".join(widget.split(".!")[2:-1])} content: {what}')
        return True

    def _check_version(self) -> None:
        """Check version of DCSpy and show message box."""
        ver_string = get_version_string(repo='emcek/dcspy', current_ver=__version__, check=True)
        self.status_txt.set(ver_string)
        if 'please update' in ver_string:
            self.master.clipboard_clear()
            self.master.clipboard_append('pip install --upgrade dcspy')
            CTkMessagebox(title='New version', message='Open Windows Command Prompt (cmd) and type:\n\npip install --upgrade dcspy\n\nNote: command copied to clipboard.')
        elif 'latest' in ver_string:
            CTkMessagebox(title='No updates', message='You are running latest version')
        elif 'failed' in ver_string:
            CTkMessagebox(title='Warning', message='Unable to check DCSpy version online', icon='warning', option_1='OK')

    def _auto_update_bios(self, silence=False) -> None:
        """
        Auto update DCS-BIOS version.

        :param silence: perform action with silence
        """
        if self.update_bios.get():
            self._update_bios(silence=silence)

    def _update_bios(self, silence=False) -> None:
        """
        Do real update Git or stable DCS-BIOS version.

        :param silence: perform action with silence
        """
        if self.git_bios_switch.get():
            self._check_bios_git(silence=silence)
        else:
            self._check_bios_release(silence=silence)

    def _check_bios_git(self, silence=False) -> None:
        """
        Check git/live version and configuration of DCS-BIOS.

        :param silence: perform action with silence
        """
        repo_dir = Path(gettempdir()) / 'dcsbios_git'
        sha = check_github_repo(git_ref=self.bios_git_ref.get(), update=True, repo_dir=repo_dir)
        LOG.debug(f'Remove: {self.bios_path.get()} ')
        rmtree(path=self.bios_path.get(), ignore_errors=True)
        LOG.debug(f'Copy Git DCS-BIOS to: {self.bios_path.get()} ')
        copytree(src=repo_dir / 'Scripts' / 'DCS-BIOS', dst=self.bios_path.get())
        local_bios = self._check_local_bios()
        self.status_txt.set(sha)
        if not silence:
            install_result = self._handling_export_lua(temp_dir=repo_dir / 'Scripts')
            install_result = f'{install_result}\n\nUsing Git/Live version.'
            CTkMessagebox(title=f'Updated {local_bios.ver}', message=install_result)

    def _check_bios_release(self, silence=False) -> None:
        """
        Check release version and configuration of DCS-BIOS.

        :param silence: perform action with silence
        """
        self._check_local_bios()
        remote_bios_info = self._check_remote_bios()
        self.status_txt.set(f'Local BIOS: {self.l_bios} | Remote BIOS: {self.r_bios}')
        correct_local_bios_ver = isinstance(self.l_bios, version.Version)
        correct_remote_bios_ver = isinstance(self.r_bios, version.Version)
        dcs_runs = proc_is_running(name='DCS.exe')
        ready_to_update = all([correct_remote_bios_ver, not dcs_runs])

        if silence and ready_to_update and not remote_bios_info.latest:
            self._update_release_bios(rel_info=remote_bios_info)
        elif not silence and ready_to_update:
            self._ask_to_update(rel_info=remote_bios_info)
        elif not all([silence, ready_to_update]):
            msg = self._get_problem_desc(correct_local_bios_ver, correct_remote_bios_ver, bool(dcs_runs))
            msg = f'{msg}\n\nUsing stable release version.'
            CTkMessagebox(title='Update', message=msg, icon='warning', option_1='OK')

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
            with open(file=Path(self.bios_path.get()) / 'lib' / 'CommonData.lua', encoding='utf-8') as cd_lua:
                cd_lua_data = cd_lua.read()
        except FileNotFoundError as err:
            LOG.debug(f'While checking DCS-BIOS version {err.__class__.__name__}: {err.filename}')
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
        msg_txt = f'You are running {self.l_bios} version.\n\n' \
                  f'Would you like to download\n' \
                  f'stable release:\n\n{rel_info.archive_file}\n\n' \
                  f'and overwrite update?'
        if not rel_info.latest:
            msg_txt = f'You are running {self.l_bios} version.\n' \
                      f'New version {rel_info.ver} available.\n' \
                      f'Released: {rel_info.published}\n\n' \
                      f'Would you like to update?'
        msg = CTkMessagebox(title='Update DCS-BIOS', message=msg_txt, icon='question', option_1='Yes', option_2='No')
        if msg.get() == 'Yes':
            self._update_release_bios(rel_info=rel_info)

    def _update_release_bios(self, rel_info: ReleaseInfo) -> None:
        """
        Perform update of release version of BIOS and check configuration.

        :param rel_info: remote release information
        """
        tmp_dir = Path(gettempdir())
        local_zip = tmp_dir / rel_info.archive_file
        download_file(url=rel_info.dl_url, save_path=local_zip)
        LOG.debug(f'Remove DCS-BIOS from: {tmp_dir} ')
        rmtree(path=tmp_dir / 'DCS-BIOS', ignore_errors=True)
        LOG.debug(f'Unpack file: {local_zip} ')
        unpack_archive(filename=local_zip, extract_dir=tmp_dir)
        LOG.debug(f'Remove: {self.bios_path.get()} ')
        rmtree(path=self.bios_path.get(), ignore_errors=True)
        LOG.debug(f'Copy DCS-BIOS to: {self.bios_path.get()} ')
        copytree(src=tmp_dir / 'DCS-BIOS', dst=self.bios_path.get())
        install_result = self._handling_export_lua(tmp_dir)
        if 'github' in install_result:
            msg = CTkMessagebox(title='Open browser', message=install_result, icon='question', option_1='Yes', option_2='No')
            if msg.get() == 'Yes':
                self._open_webpage(r'https://github.com/DCSFlightpanels/DCSFlightpanels/wiki/Installation')
        else:
            local_bios = self._check_local_bios()
            self.status_txt.set(f'Local BIOS: {local_bios.ver} | Remote BIOS: {self.r_bios}')
            install_result = f'{install_result}\n\nUsing stable release version.'
            CTkMessagebox(title=f'Updated {local_bios.ver}', message=install_result)

    def _handling_export_lua(self, temp_dir: Path) -> str:
        """
        Check if Export.lua file exist and its content.

        If not copy Export.lua from DCS-BIOS installation archive.

        :param temp_dir: directory with DCS-BIOS archive
        :return: result of checks
        """
        result = 'Installation Success. Done.'
        lua_dst_path = Path(self.bios_path.get()).parent
        lua = 'Export.lua'
        try:
            with open(file=lua_dst_path / lua, encoding='utf-8') as lua_dst:
                lua_dst_data = lua_dst.read()
        except FileNotFoundError as err:
            LOG.debug(f'{err.__class__.__name__}: {err.filename}')
            copy(src=temp_dir / lua, dst=lua_dst_path)
            LOG.debug(f'Copy Export.lua from: {temp_dir} to {lua_dst_path} ')
        else:
            result += check_dcs_bios_entry(lua_dst_data, lua_dst_path, temp_dir)
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
        self._save_cfg()
        app_params = {'lcd_type': LCD_TYPES[keyboard]['type'], 'event': self.event}
        app_thread = Thread(target=dcspy_run, kwargs=app_params)
        app_thread.name = 'dcspy-app'
        LOG.debug(f'Starting thread {app_thread} for: {app_params}')
        self.status_txt.set('You can close GUI')
        self.btn_start.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.ACTIVE)
        app_thread.start()

#!/usr/bin/env python
from functools import partial
from logging import getLogger
from pathlib import Path
from threading import Event

import customtkinter
from PIL import Image
from pystray import Icon, MenuItem

from dcspy import LCD_TYPES, config
from dcspy.starter import dcspy_run
from dcspy.tk_gui import DcspyGui
from dcspy.utils import check_dcs_ver

LOG = getLogger(__name__)
__version__ = '2.0.0'


def _quit_window(window: customtkinter.CTk, icon: Icon, menu: MenuItem):
    """
    Quit application.

    :param window: main window
    :param icon: icon instance
    :param menu: menu item instance
    """
    LOG.debug(f'Icon: {icon.name}, Menu: {menu.text}')
    icon.visible = False
    icon.stop()
    window.quit()


def _show_window(window: customtkinter.CTk, icon: Icon, menu: MenuItem):
    """
    Show main application window.

    :param window: main window
    :param icon: icon instance
    :param menu: menu item instance
    """
    LOG.debug(f'Icon: {icon.name}, Menu: {menu.text}')
    window.after(0, window.deiconify)


def _withdraw_window(window: customtkinter.CTk):
    """
    Withdraw main application window.

    :param window: main window
    """
    window.withdraw()


def run():
    """Start DCSpy GUI."""
    if config['show_gui']:
        customtkinter.set_appearance_mode(config['theme_mode'])
        customtkinter.set_default_color_theme(config['theme_color'])
        LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
        dcs_type, dcs_ver = check_dcs_ver(Path(str(config["dcs"])))
        LOG.info(f'DCS {dcs_type} ver: {dcs_ver}')
        root = customtkinter.CTk()
        width, height = 770, 500
        root.geometry(f'{width}x{height}')
        root.minsize(width=width, height=height)
        root.iconbitmap(Path(__file__).resolve().with_name('dcspy.ico'))
        if config['theme_mode'] == 'dark':
            root.iconbitmap(Path(__file__).resolve().with_name('dcspy_white.ico'))
        root.title('DCSpy')

        image = Image.open(Path(__file__).resolve().with_name('dcspy.ico'))
        menu = (MenuItem('Quit', partial(_quit_window, root)), MenuItem('Show', partial(_show_window, root)))
        icon = Icon('dcspy', image, 'DCSpy', menu)
        root.protocol('WM_DELETE_WINDOW', partial(_withdraw_window, root))
        icon.run_detached()

        DcspyGui(master=root)
        root.mainloop()
    else:
        dcspy_run(lcd_type=LCD_TYPES[config['keyboard']]['type'], event=Event())


if __name__ == '__main__':
    run()

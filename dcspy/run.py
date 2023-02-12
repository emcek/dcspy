from logging import getLogger
from os import path
from threading import Event

import customtkinter

from dcspy import config, LCD_TYPES
from dcspy.starter import dcspy_run
from dcspy.tk_gui import DcspyGui
from dcspy.utils import check_dcs_ver

LOG = getLogger(__name__)
__version__ = '1.8.1'


def run():
    """Function to start DCSpy GUI."""
    if config['show_gui']:
        customtkinter.set_appearance_mode(config['theme_mode'])
        customtkinter.set_default_color_theme(config['theme_color'])
        LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
        dcs_type, dcs_ver = check_dcs_ver(config["dcs"])
        LOG.info(f'DCS {dcs_type} ver: {dcs_ver}')
        root = customtkinter.CTk()
        width, height = 770, 500
        root.geometry(f'{width}x{height}')
        root.minsize(width=width, height=height)
        here = path.abspath(path.dirname(__file__))
        root.iconbitmap(path.join(here, 'resources', 'dcspy.ico'))
        if config['theme_mode'] == 'dark':
            root.iconbitmap(path.join(here, 'resources', 'dcspy_white.ico'))
        root.title('DCSpy')
        DcspyGui(master=root, config_file=path.join(here, 'resources', 'config.yaml'))
        root.mainloop()
    else:
        dcspy_run(lcd_type=LCD_TYPES[config['keyboard']]['type'], event=Event())


if __name__ == '__main__':
    run()

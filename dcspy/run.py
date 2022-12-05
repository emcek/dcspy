from logging import getLogger
from os import path
from threading import Event

import customtkinter

from dcspy import config, LCD_TYPES
from dcspy.starter import dcspy_run
from dcspy.tk_gui import DcspyGui
from dcspy.utils import check_dcs_ver

LOG = getLogger(__name__)
__version__ = '1.7.5'
customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


def run():
    """Function to start DCSpy GUI."""
    if config['show_gui']:
        LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
        dcs_type, dcs_ver = check_dcs_ver(config["dcs"])
        LOG.info(f'DCS {dcs_type} ver: {dcs_ver}')
        root = customtkinter.CTk()
        width, height = 210, 160
        root.geometry(f'{width}x{height}')
        root.minsize(width=width, height=height)
        here = path.abspath(path.dirname(__file__))
        root.iconbitmap(default=path.join(here, 'dcspy.ico'))
        root.title('DCSpy')
        DcspyGui(master=root, config_file=path.join(here, 'config.yaml'))
        root.mainloop()
    else:
        dcspy_run(lcd_type=LCD_TYPES[config['keyboard']['type']], event=Event())


if __name__ == '__main__':
    run()

from os import environ, unlink
from pathlib import Path
from tempfile import gettempdir

import customtkinter

from dcspy import config
from dcspy.tk_gui import DcspyGui
from dcspy.utils import check_dcs_ver

LOG = getLogger(__name__)
__version__ = '2.3.2'


def run() -> None:
    """Start DCSpy GUI."""
    customtkinter.set_appearance_mode(config['theme_mode'])
    customtkinter.set_default_color_theme(config['theme_color'])
    root = customtkinter.CTk()
    width, height = 770, 520
    root.geometry(f'{width}x{height}')
    root.minsize(width=width, height=height)
    root.iconbitmap(Path(__file__).resolve() / '..' / 'img' / 'dcspy.ico')
    if config['theme_mode'] == 'dark':
        root.iconbitmap(Path(__file__).resolve() / '..' / 'img' / 'dcspy_white.ico')
    root.title('DCSpy')
    DcspyGui(master=root)
    if not config['show_gui']:
        root.withdraw()
    try:
        unlink(Path(gettempdir()) / f'onefile_{environ["NUITKA_ONEFILE_PARENT"]}_splash_feedback.tmp')
    except (KeyError, FileNotFoundError):
        pass
    root.mainloop()


if __name__ == '__main__':
    run()

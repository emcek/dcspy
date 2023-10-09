from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Sequence, Tuple, Union

from PIL import ImageFont
from pydantic import BaseModel, RootModel, field_validator

# Network
SEND_ADDR = ('127.0.0.1', 7778)
RECV_ADDR = ('', 5010)
MULTICAST_IP = '239.255.50.10'

# LCD types
TYPE_MONO = 1
TYPE_COLOR = 2

# LCD Monochrome size
MONO_WIDTH = 160
MONO_HEIGHT = 43

# LCD Color size
COLOR_WIDTH = 320
COLOR_HEIGHT = 240

# LED constants
LOGI_LED_DURATION_INFINITE = 0
LOGI_DEVICETYPE_MONOCHROME = 1
LOGI_DEVICETYPE_RGB = 2
LOGI_DEVICETYPE_ALL = LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB

# G Key
LOGITECH_MAX_GKEYS = 30
LOGITECH_MAX_M_STATES = 4

# Others
LOCAL_APPDATA = True
DCSPY_REPO_NAME = 'emcek/dcspy'
DCS_BIOS_REPO_DIR = Path(gettempdir()) / 'dcsbios_git'
CTRL_LIST_SEPARATOR = '--'
SUPPORTED_CRAFTS = {
    'FA18Chornet': {'name': 'F/A-18C Hornet', 'bios': 'FA-18C_hornet'},
    'Ka50': {'name': 'Ka-50 Black Shark II', 'bios': 'Ka-50'},
    'Ka503': {'name': 'Ka-50 Black Shark III', 'bios': 'Ka-50_3'},
    'Mi8MT': {'name': 'Mi-8MTV2 Magnificent Eight', 'bios': 'Mi-8MT'},
    'Mi24P': {'name': 'Mi-24P Hind', 'bios': 'Mi-24P'},
    'F16C50': {'name': 'F-16C Viper', 'bios': 'F-16C_50'},
    'F15ESE': {'name': 'F-15ESE Eagle', 'bios': 'F-15ESE'},
    'AH64DBLKII': {'name': 'AH-64D Apache', 'bios': 'AH-64D_BLK_II'},
    'A10C': {'name': 'A-10C Warthog', 'bios': 'A-10C'},
    'A10C2': {'name': 'A-10C II Tank Killer', 'bios': 'A-10C_2'},
    'F14A135GR': {'name': 'F-14A Tomcat', 'bios': 'F-14A-135-GR'},
    'F14B': {'name': 'F-14B Tomcat', 'bios': 'F-14B'},
    'AV8BNA': {'name': 'AV-8B N/A Harrier', 'bios': 'AV8BNA'},
}


class Input(BaseModel):
    description: str

    def get(self, attribute: str, default=None) -> Optional[Any]:
        """
        Access attribute and get default when is not available.

        :param attribute:
        :param default:
        :return:
        """
        return self.model_dump().get(attribute, default)


class FixedStep(Input):
    interface: str = 'fixed_step'

    @field_validator('interface')
    def validate_interface(cls, value):
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'fixed_step':
            raise ValueError("Invalid value for 'interface'. Only 'fixed_step' is allowed.")
        return value


class VariableStep(Input):
    interface: str = 'variable_step'
    max_value: int
    suggested_step: int

    @field_validator('interface')
    def validate_interface(cls, value):
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'variable_step':
            raise ValueError("Invalid value for 'interface'. Only 'variable_step' is allowed.")
        return value


class SetState(Input):
    interface: str = 'set_state'
    max_value: int

    @field_validator('interface')
    def validate_interface(cls, value):
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'set_state':
            raise ValueError("Invalid value for 'interface'. Only 'set_state' is allowed.")
        return value


class Action(Input):
    argument: str
    interface: str = 'action'

    @field_validator('interface')
    def validate_interface(cls, value):
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'action':
            raise ValueError("Invalid value for 'interface'. Only 'action' is allowed.")
        return value


class Output(BaseModel):
    address: int
    description: str
    suffix: str


class OutputStr(Output):
    max_length: int
    type: str

    @field_validator('type')
    def validate_interface(cls, value):
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'string':
            raise ValueError("Invalid value for 'interface'. Only 'string' is allowed.")
        return value


class OutputInt(Output):
    mask: int
    max_value: int
    shift_by: int
    type: str

    @field_validator('type')
    def validate_interface(cls, value):
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'integer':
            raise ValueError("Invalid value for 'interface'. Only 'integer' is allowed.")
        return value


# ---------------- DCS-BIOS ----------------
class IntBuffArgs(BaseModel):
    address: int
    mask: int
    shift_by: int


class BiosValueInt(BaseModel):
    klass: str
    args: IntBuffArgs
    value: Union[int, str]
    max_value: int


class StrBuffArgs(BaseModel):
    address: int
    max_length: int


class BiosValueStr(BaseModel):
    klass: str
    args: StrBuffArgs
    value: Union[int, str]


class BiosValue(RootModel):
    root: Dict[str, Union[BiosValueStr, BiosValueInt]]
# ---------------- DCS-BIOS ----------------


class ControlKeyData:
    def __init__(self, name: str, description: str, max_value: int, suggested_step: int = 1) -> None:
        """
        Define type of input for cockpit controller.

        :param name: name of the input
        :param description: short description
        :param max_value: max value (zero based)
        :param suggested_step: 1 by default
        """
        self.name = name
        self.description = description
        self.max_value = max_value
        self.suggested_step = suggested_step
        self.list_dict: List[Union[FixedStep, VariableStep, SetState, Action]] = []

    def __repr__(self) -> str:
        return f'KeyControl({self.name}: {self.description} - max_value={self.max_value}, suggested_step={self.suggested_step})'

    def __bool__(self) -> bool:
        if not all([self.max_value, self.suggested_step]):
            return False
        return True

    @classmethod
    def from_dicts(cls, /, name, description, list_of_dicts: List[Union[FixedStep, VariableStep, SetState, Action]]) -> 'ControlKeyData':
        """
        Construct object from list of dictionaries.

        :param name: name of the input
        :param description: short description
        :param list_of_dicts:
        :return: ControlKeyData instance
        """
        try:
            max_value = cls._get_max_value(list_of_dicts)
            suggested_step = max(d.get('suggested_step', 1) for d in list_of_dicts)
        except ValueError:
            max_value = 0
            suggested_step = 0
        instance = cls(name=name, description=description, max_value=max_value, suggested_step=suggested_step)
        instance.list_dict = list_of_dicts
        return instance

    @staticmethod
    def _get_max_value(list_of_dicts: List[Union[FixedStep, VariableStep, SetState, Action]]) -> int:
        """
        Get max value from list of dictionaries.

        :param list_of_dicts:
        :return: max value
        """
        _real_zero = False
        _max_values = []
        for d in list_of_dicts:
            try:
                _max_values.append(d.max_value)
                if d.max_value == 0:
                    _real_zero = True
                    break
            except AttributeError:
                _max_values.append(0)
        max_value = max(_max_values)
        if all([not _real_zero, not max_value]):
            max_value = 1
        return max_value

    def request(self) -> Union[str, Dict[str, Union[str, Iterator]]]:
        """
        Generate button request for input.

        :return: str or dict with iterator
        """
        if self.is_cycle:
            return {'bios': self.name, 'iter': iter([0])}
        elif self.one_input and self.has_fixed_step:
            return f'{self.name} INC\n'   # todo: if 2 buttons/keys in one mode has the same name used 1st will be INC, 2nd DEC
        elif self.has_set_state and self.has_action:
            return f'{self.name} {self.max_value-self.suggested_step}\n|{self.name} {self.max_value}\n'  # 0 1
        elif self.has_fixed_step and self.has_set_state and self.max_value == 0:
            return f'{self.name} 0\n'

    @property
    def cycle_data(self):
        """
        Get cycle data. Used for cycle buttons.

        :return: tuple with max value and suggested step
        """
        return self.max_value, self.suggested_step

    @property
    def is_cycle(self) -> bool:
        """
        Check if input is cycle button.

        :return: bool if input is cycle button, False otherwise.
        """
        if self.has_set_state and self.max_value > 0:
            return True
        elif self.has_variable_step:
            return True
        elif self.has_fixed_step and self.has_action and self.input_len == 2:
            return True
        elif self.has_action and self.one_input:
            return True
        return False

    @property
    def input_len(self) -> int:
        """
        Get length of input dictionary.

        :return: int
        """
        return len(self.list_dict)

    @property
    def one_input(self) -> bool:
        """
        Check if input has only one input dict.

        :return: bool
        """
        return bool(len(self.list_dict) == 1)

    @property
    def has_fixed_step(self) -> bool:
        """
        Check if input has fixed step input.

        :return: bool
        """
        return any([isinstance(d, FixedStep) for d in self.list_dict])

    @property
    def has_variable_step(self) -> bool:
        """
        Check if input has variable step input.

        :return: bool
        """
        return any([isinstance(d, VariableStep) for d in self.list_dict])

    @property
    def has_set_state(self) -> bool:
        """
        Check if input has set state input.

        :return: bool
        """
        return any([isinstance(d, SetState) for d in self.list_dict])

    @property
    def has_action(self) -> bool:
        """
        Check if input has action input.

        :return: bool
        """
        return any([isinstance(d, Action) for d in self.list_dict])


class Control(BaseModel):
    api_variant: Optional[str] = None
    category: str
    control_type: str
    description: str
    identifier: str
    inputs: List[Union[FixedStep, VariableStep, SetState, Action]]
    momentary_positions: Optional[str] = None
    outputs: List[Union[OutputStr, OutputInt]]
    physical_variant: Optional[str] = None

    @property
    def input(self) -> ControlKeyData:
        """
        Extract inputs data.

        :return: ControlKeyData
        """
        return ControlKeyData.from_dicts(name=self.identifier, description=self.description, list_of_dicts=self.inputs)

    @property
    def output(self) -> Union[BiosValueInt, BiosValueStr]:
        """
        Extract outputs data.

        :return: Union[BiosValueInt, BiosValueStr]
        """
        if isinstance(self.outputs[0], OutputInt):
            return BiosValueInt(klass='IntegerBuffer',
                                args=IntBuffArgs(address=self.outputs[0].address, mask=self.outputs[0].mask, shift_by=self.outputs[0].shift_by),
                                value=int(),
                                max_value=self.outputs[0].max_value)
        else:
            return BiosValueStr(klass='StringBuffer',
                                args=StrBuffArgs(address=self.outputs[0].address, max_length=self.outputs[0].max_length),
                                value='')


# DcsBios = RootModel(Dict[str, Dict[str, Control]])

class DcsBios(RootModel):
    root: Dict[str, Dict[str, Control]]

    def __str__(self) -> str:
        return str(self.root)

    def __getitem__(self, item):
        # https://github.com/pydantic/pydantic/issues/1802
        return self.root[item]

    def get(self, item, default=None):
        """
        Access item and get default when is not available.

        :param item:
        :param default:
        :return:
        """
        return getattr(self.root, item, default)


class GuiPlaneInputRequest(BaseModel):
    identifier: str
    request: str
    widget_iface: str


class LcdButton(Enum):
    """LCD Buttons."""
    NONE = 0x0
    ONE = 0x1
    TWO = 0x2
    THREE = 0x4
    FOUR = 0x8
    LEFT = 0x100
    RIGHT = 0x200
    OK = 0x400
    CANCEL = 0x800
    UP = 0x1000
    DOWN = 0x2000
    MENU = 0x4000


class LcdType(Enum):
    """LCD Type."""
    MONO = TYPE_MONO
    COLOR = TYPE_COLOR


class LcdMode(Enum):
    """LCD Mode."""
    BLACK_WHITE = '1'
    TRUE_COLOR = 'RGBA'


@dataclass
class LcdInfo:
    """LCD info."""
    width: int
    height: int
    type: LcdType
    foreground: Union[int, Tuple[int, int, int, int]]
    background: Union[int, Tuple[int, int, int, int]]
    mode: LcdMode
    font_xs: ImageFont.FreeTypeFont
    font_s: ImageFont.FreeTypeFont
    font_l: ImageFont.FreeTypeFont


KEYBOARD_TYPES = ['G19', 'G510', 'G15v1', 'G15v2', 'G13']


class KeyboardModel(BaseModel):
    name: str
    klass: str
    modes: int
    gkeys: int
    lcdkeys: int
    lcd: str


ModelG19 = KeyboardModel(name='G19', klass='G19', modes=3, gkeys=12, lcdkeys=7, lcd='color')
ModelG13 = KeyboardModel(name='G13', klass='G13', modes=3, gkeys=29, lcdkeys=4, lcd='mono')
ModelG15v1 = KeyboardModel(name='G15 v1', klass='G15v1', modes=3, gkeys=18, lcdkeys=4, lcd='mono')
ModelG15v2 = KeyboardModel(name='G15 v2', klass='G15v2', modes=3, gkeys=6, lcdkeys=4, lcd='mono')
ModelG510 = KeyboardModel(name='G510', klass='G510', modes=3, gkeys=18, lcdkeys=4, lcd='mono')


@dataclass
class Gkey:
    """Logitech G-Key."""
    key: int
    mode: int

    def __str__(self):
        """Return with format G<i>/M<j>."""
        return f'G{self.key}/M{self.mode}'

    def __bool__(self):
        """Return False when any of value is zero."""
        return all([self.key, self.mode])

    def __hash__(self):
        """Hash will be the same for any two Gkey instances with the same key and mode values."""
        return hash((self.key, self.mode))

    def to_dict(self):
        """
        Convert Gkey into dict.

        :return: ex. {'g_key': 2, 'mode': 1}
        """
        return {'g_key': self.key, 'mode': self.mode}


def generate_gkey(key: int, mode: int) -> Sequence[Gkey]:
    """
    Generate sequence of G-Keys.

    :param key: number of keys
    :param mode: number of modes
    :return:
    """
    return tuple([Gkey(k, m) for k in range(1, key + 1) for m in range(1, mode + 1)])


class MsgBoxTypes(Enum):
    INFO = 'information'
    QUESTION = 'question'
    WARNING = 'warning'
    CRITICAL = 'critical'
    ABOUT = 'about'
    ABOUT_QT = 'aboutQt'


class SystemData(NamedTuple):
    """Tuple to store system related information."""
    system: str
    release: str
    ver: str
    proc: str
    dcs_type: str
    dcs_ver: str
    dcspy_ver: str
    bios_ver: str
    dcs_bios_ver: str
    git_ver: str

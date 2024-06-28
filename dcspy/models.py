from collections.abc import Iterator, Mapping, Sequence
from enum import Enum
from functools import partial
from pathlib import Path
from re import search
from tempfile import gettempdir
from typing import Any, Callable, Final, Optional, TypedDict, Union

from packaging import version
from PIL import Image, ImageFont
from pydantic import BaseModel, ConfigDict, RootModel, field_validator

# Network
SEND_ADDR: Final = ('127.0.0.1', 7778)
UDP_PORT: Final = 5010
RECV_ADDR: Final = ('', UDP_PORT)
MULTICAST_IP: Final = '239.255.50.10'

# G Key
LOGITECH_MAX_GKEYS: Final = 30
LOGITECH_MAX_M_STATES: Final = 4

# Key press
KEY_DOWN: Final = 1
KEY_UP: Final = 0

# Others
NO_OF_LCD_SCREENSHOTS: Final = 301
TIME_BETWEEN_REQUESTS: Final = 0.2
LOCAL_APPDATA: Final = True
DCSPY_REPO_NAME: Final = 'emcek/dcspy'
DEFAULT_FONT_NAME: Final = 'consola.ttf'
DCS_BIOS_REPO_DIR: Final = Path(gettempdir()) / 'dcsbios_git'
DCS_BIOS_VER_FILE: Final = 'bios_live_ver.txt'
CTRL_LIST_SEPARATOR: Final = '--'
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
    'F4E45MC': {'name': 'F-4E Phantom II', 'bios': 'F-4E-45MC'},
}


class AircraftKwargs(TypedDict):
    """
    Represent the keyword arguments expected by the Aircraft class.

    :param update_display: Callable[[Image.Image], None]
    :param bios_data: Mapping[str, Union[str, int]]
    """
    update_display: Callable[[Image.Image], None]
    bios_data: Mapping[str, Union[str, int]]


class Input(BaseModel):
    """Input base class of inputs section of Control."""
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
    """FixedStep input interface of inputs a section of Control."""
    interface: str = 'fixed_step'

    @field_validator('interface')
    def validate_interface(cls, value: str) -> str:
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'fixed_step':
            raise ValueError("Invalid value for 'interface'. Only 'fixed_step' is allowed.")
        return value


class VariableStep(Input):
    """VariableStep input interface of inputs section of Control."""
    interface: str = 'variable_step'
    max_value: int
    suggested_step: int

    @field_validator('interface')
    def validate_interface(cls, value: str) -> str:
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'variable_step':
            raise ValueError("Invalid value for 'interface'. Only 'variable_step' is allowed.")
        return value


class SetState(Input):
    """SetState input interface of inputs section of Control."""
    interface: str = 'set_state'
    max_value: int

    @field_validator('interface')
    def validate_interface(cls, value: str) -> str:
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'set_state':
            raise ValueError("Invalid value for 'interface'. Only 'set_state' is allowed.")
        return value


class Action(Input):
    """Action input interface of inputs section of Control."""
    argument: str
    interface: str = 'action'

    @field_validator('interface')
    def validate_interface(cls, value: str) -> str:
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'action':
            raise ValueError("Invalid value for 'interface'. Only 'action' is allowed.")
        return value


class SetString(Input):
    """SetString input interface of inputs a section of Control."""
    interface: str = 'set_string'

    @field_validator('interface')
    def validate_interface(cls, value: str) -> str:
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'set_string':
            raise ValueError("Invalid value for 'interface'. Only 'set_string' is allowed.")
        return value


class Output(BaseModel):
    """Output base class of outputs section of Control."""
    address: int
    description: str
    suffix: str


class OutputStr(Output):
    """String output interface of outputs a section of Control."""
    max_length: int
    type: str

    @field_validator('type')
    def validate_interface(cls, value: str) -> str:
        """
        Validate.

        :param value:
        :return:
        """
        if value != 'string':
            raise ValueError("Invalid value for 'interface'. Only 'string' is allowed.")
        return value


class OutputInt(Output):
    """Integer output interface of outputs section of Control."""
    mask: int
    max_value: int
    shift_by: int
    type: str

    @field_validator('type')
    def validate_interface(cls, value: str) -> str:
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
    """Arguments of BIOS Integer Buffer."""
    address: int
    mask: int
    shift_by: int


class BiosValueInt(BaseModel):
    """Value of BIOS Integer Buffer."""
    klass: str
    args: IntBuffArgs
    value: Union[int, str]
    max_value: int


class StrBuffArgs(BaseModel):
    """Arguments of BIOS String Buffer."""
    address: int
    max_length: int


class BiosValueStr(BaseModel):
    """Value of BIOS String Buffer."""
    klass: str
    args: StrBuffArgs
    value: Union[int, str]


class ControlDepiction(BaseModel):
    """Represent the depiction of a control."""
    name: str
    description: str


class ControlKeyData:
    """Describes input data for cockpit controller."""

    def __init__(self, name: str, description: str, max_value: int, suggested_step: int = 1) -> None:
        """
        Define a type of input for cockpit controller.

        :param name: Name of the input
        :param description: Short description
        :param max_value: Max value (zero based)
        :param suggested_step: One (1) by default
        """
        self.name = name
        self.description = description
        self.max_value = max_value
        self.suggested_step = suggested_step
        self.list_dict: list[Union[FixedStep, VariableStep, SetState, Action, SetString]] = []

    def __repr__(self) -> str:
        return f'KeyControl({self.name}: {self.description} - max_value={self.max_value}, suggested_step={self.suggested_step}'

    def __bool__(self) -> bool:
        if not all([self.max_value, self.suggested_step]):
            return False
        return True

    @classmethod
    def from_control(cls, /, ctrl: 'Control') -> 'ControlKeyData':
        """
        Construct object based on Control BIOS model.

        :param ctrl: Control BIOS model
        :return: ControlKeyData instance
        """
        try:
            max_value = cls._get_max_value(ctrl.inputs)
            suggested_step: int = max(d.get('suggested_step', 1) for d in ctrl.inputs)  # type: ignore
        except ValueError:
            max_value = 0
            suggested_step = 0
        instance = cls(name=ctrl.identifier, description=ctrl.description, max_value=max_value, suggested_step=suggested_step)
        instance.list_dict = ctrl.inputs
        return instance

    @staticmethod
    def _get_max_value(list_of_dicts: list[Union[FixedStep, VariableStep, SetState, Action, SetString]]) -> int:
        """
        Get a maximum value from a list of dictionaries.

        :param list_of_dicts: List of inputs
        :return: Maximum value of all inputs
        """
        max_value, real_zero = ControlKeyData.__get_max(list_of_dicts)
        if all([not real_zero, not max_value]):
            max_value = 1
        return max_value

    @staticmethod
    def __get_max(list_of_dicts: list[Union[FixedStep, VariableStep, SetState, Action, SetString]]) -> tuple[int, bool]:
        """
        Maximum value found in the 'max_value' attribute of the objects in the list.

        Check if any of the objects had a 'max_value' of 0.

        :param list_of_dicts: List of dictionaries containing objects of types FixedStep, VariableStep, SetState, Action, SetString.
        :return: A tuple containing the maximum value and a boolean value indicating if any of the objects had a 'max_value' of 0.
        """
        __real_zero = False
        __max_values = []
        for d in list_of_dicts:
            try:
                __max_values.append(d.max_value)  # type: ignore[union-attr]
                if d.max_value == 0:  # type: ignore[union-attr]
                    __real_zero = True
                    break
            except AttributeError:
                __max_values.append(0)
        return max(__max_values), __real_zero

    @property
    def depiction(self) -> ControlDepiction:
        """
        Return the depiction of the control.

        :return: ControlDepiction object representing the control's name amd description.
        """
        return ControlDepiction(name=self.name, description=self.description)

    @property
    def input_len(self) -> int:
        """
        Get a length of input dictionary.

        :return: Number of inputs as integer
        """
        return len(self.list_dict)

    @property
    def one_input(self) -> bool:
        """
        Check if input has only one input dict.

        :return: True if ControlKeyData has only one input, False otherwise
        """
        return bool(len(self.list_dict) == 1)

    @property
    def has_fixed_step(self) -> bool:
        """
        Check if input has fixed step input.

        :return: True if ControlKeyData has fixed step input, False otherwise
        """
        return any(isinstance(d, FixedStep) for d in self.list_dict)

    @property
    def has_variable_step(self) -> bool:
        """
        Check if input has variable step input.

        :return: True if ControlKeyData has variable step input, False otherwise
        """
        return any(isinstance(d, VariableStep) for d in self.list_dict)

    @property
    def has_set_state(self) -> bool:
        """
        Check if input has set state input.

        :return: True if ControlKeyData has set state input, False otherwise
        """
        return any(isinstance(d, SetState) for d in self.list_dict)

    @property
    def has_action(self) -> bool:
        """
        Check if input has action input.

        :return: True if ControlKeyData has action input, False otherwise
        """
        return any(isinstance(d, Action) for d in self.list_dict)

    @property
    def has_set_string(self) -> bool:
        """
        Check if input has set string input.

        :return: True if ControlKeyData has set string input, False otherwise
        """
        return any(isinstance(d, SetString) for d in self.list_dict)

    @property
    def is_push_button(self) -> bool:
        """
        Check if the controller is a push button type.

        :return: True if controller is a push button type, False otherwise
        """
        return self.has_fixed_step and self.has_set_state and self.max_value == 1


class Control(BaseModel):
    """Control section of the BIOS model."""
    api_variant: Optional[str] = None
    category: str
    control_type: str
    description: str
    identifier: str
    inputs: list[Union[FixedStep, VariableStep, SetState, Action, SetString]]
    outputs: list[Union[OutputStr, OutputInt]]

    @property
    def input(self) -> ControlKeyData:
        """
        Extract inputs data.

        :return: ControlKeyData
        """
        return ControlKeyData.from_control(ctrl=self)

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


class DcsBiosPlaneData(RootModel):
    """DcsBios plane data model."""
    root: dict[str, dict[str, Control]]

    def get_ctrl(self, ctrl_name: str) -> Optional[Control]:
        """
        Get Control from DCS-BIOS with name.

        :param ctrl_name: Control name
        :return: Control instance
        """
        for controllers in self.root.values():
            for ctrl, data in controllers.items():
                if ctrl == ctrl_name:
                    return Control.model_validate(data)
        return None

    def get_inputs(self) -> dict[str, dict[str, ControlKeyData]]:
        """
        Get dict with all not empty inputs for plane.

        Inputs are grouped in original sections.

        :return: Dict with sections and ControlKeyData models.
        """
        ctrl_key: dict[str, dict[str, ControlKeyData]] = {}

        for section, controllers in self.root.items():
            ctrl_key[section] = {}
            for ctrl, data in controllers.items():
                ctrl_input = Control.model_validate(data).input
                if ctrl_input and not ctrl_input.has_set_string:
                    ctrl_key[section][ctrl] = ctrl_input
            if not ctrl_key[section]:
                del ctrl_key[section]
        return ctrl_key


class CycleButton(BaseModel):
    """Map BIOS key string with iterator to keep current value."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ctrl_name: str
    step: int = 1
    max_value: int = 1
    iter: Iterator[int] = iter([0])

    @classmethod
    def from_request(cls, /, req: str) -> 'CycleButton':
        """
        Use BIOS request string from plane configuration yaml.

        :param req: BIOS request string
        """
        selector, _, step, max_value = req.split(' ')
        return CycleButton(ctrl_name=selector, step=int(step), max_value=int(max_value))

    def __bool__(self) -> bool:
        """Return True if any of the attributes: `step`, `max_value`, `ctrl_name` is truthy, False otherwise."""
        return not all([not self.step, not self.max_value, not self.ctrl_name])


class GuiPlaneInputRequest(BaseModel):
    """Input request for Control for GUI."""
    identifier: str
    request: str
    widget_iface: str

    @classmethod
    def from_control_key(cls, ctrl_key: ControlKeyData, rb_iface: str, custom_value: str = '') -> 'GuiPlaneInputRequest':
        """
        Generate GuiPlaneInputRequest from ControlKeyData and radio button widget.

        :param ctrl_key: ControlKeyData
        :param rb_iface: widget interface
        :param custom_value: custom request
        :return: GuiPlaneInputRequest
        """
        rb_iface_request = {
            'rb_action': f'{ctrl_key.name} TOGGLE',
            'rb_fixed_step_inc': f'{ctrl_key.name} INC',
            'rb_fixed_step_dec': f'{ctrl_key.name} DEC',
            'rb_cycle': f'{ctrl_key.name} CYCLE {ctrl_key.suggested_step} {ctrl_key.max_value}',
            'rb_custom': f'{ctrl_key.name} {RequestType.CUSTOM.value} {custom_value}',
            'rb_push_button': f'{ctrl_key.name} {RequestType.PUSH_BUTTON.value}',
            'rb_variable_step_plus': f'{ctrl_key.name} +{ctrl_key.suggested_step}',
            'rb_variable_step_minus': f'{ctrl_key.name} -{ctrl_key.suggested_step}',
            'rb_set_state': f'{ctrl_key.name} {custom_value}',
        }
        return cls(identifier=ctrl_key.name, request=rb_iface_request[rb_iface], widget_iface=rb_iface)

    @classmethod
    def from_plane_gkeys(cls, /, plane_gkeys: dict[str, str]) -> dict[str, 'GuiPlaneInputRequest']:
        """
        Generate GuiPlaneInputRequest from plane_gkeys yaml.

        :param plane_gkeys:
        :return:
        """
        input_reqs = {}
        req_keyword_rb_iface = {
            RequestType.CUSTOM.value: 'rb_custom',
            RequestType.PUSH_BUTTON.value: 'rb_push_button',
            'TOGGLE': 'rb_action',
            'INC': 'rb_fixed_step_inc',
            'DEC': 'rb_fixed_step_dec',
            'CYCLE': 'rb_cycle',
            '+': 'rb_variable_step_plus',
            '-': 'rb_variable_step_minus',
            ' ': 'rb_set_state',
        }

        for gkey, data in plane_gkeys.items():
            try:
                iface = next(rb_iface for req_suffix, rb_iface in req_keyword_rb_iface.items() if req_suffix in data)
            except StopIteration:
                data = ''
                iface = ''
            input_reqs[gkey] = GuiPlaneInputRequest(identifier=data.split(' ')[0], request=data, widget_iface=iface)
        return input_reqs

    @classmethod
    def make_empty(cls) -> 'GuiPlaneInputRequest':
        """Make empty GuiPlaneInputRequest."""
        return cls(identifier='', request='', widget_iface='')


class LedConstants(Enum):
    """LED constants."""
    LOGI_LED_DURATION_INFINITE: Final = 0
    LOGI_DEVICETYPE_MONOCHROME: Final = 1
    LOGI_DEVICETYPE_RGB: Final = 2
    LOGI_DEVICETYPE_ALL: Final = 3  # LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB


class LcdButton(Enum):
    """LCD Buttons."""
    NONE: Final = 0x0
    ONE: Final = 0x1
    TWO: Final = 0x2
    THREE: Final = 0x4
    FOUR: Final = 0x8
    LEFT: Final = 0x100
    RIGHT: Final = 0x200
    OK: Final = 0x400
    CANCEL: Final = 0x800
    UP: Final = 0x1000
    DOWN: Final = 0x2000
    MENU: Final = 0x4000

    def __str__(self) -> str:
        return self.name


class MouseButton(BaseModel):
    """LCD Buttons."""
    button: int = 0

    def __str__(self) -> str:
        return f'M_{self.button}'

    def __bool__(self) -> bool:
        """Return False when button value is zero."""
        return bool(self.button)

    def __hash__(self) -> int:
        """Hash will be the same for any two MouseButton instances with the same button value."""
        return hash(self.button)

    @classmethod
    def from_yaml(cls, /, yaml_str: str) -> 'MouseButton':
        """
        Construct MouseButton from YAML string.

        :param yaml_str: MouseButton string, example: M_3
        :return: MouseButton instance
        """
        match = search(r'M_(\d+)', yaml_str)
        if match:
            return cls(button=int(match.group(1)))
        raise ValueError(f'Invalid MouseButton format: {yaml_str}. Expected: M_<i>')

    @staticmethod
    def generate(button_range: tuple[int, int]) -> Sequence['MouseButton']:
        """
        Generate a sequence of MouseButton-Keys.

        :param button_range: Start and stop (inclusive) of range for mouse buttons
        """
        return tuple([MouseButton(button=m) for m in range(button_range[0], button_range[1] + 1)])


class LcdType(Enum):
    """LCD Type."""
    NONE: Final = 0
    MONO: Final = 1
    COLOR: Final = 2


class LcdSize(Enum):
    """LCD dimensions."""
    NONE: Final = 0
    MONO_WIDTH: Final = 160
    MONO_HEIGHT: Final = 43
    COLOR_WIDTH: Final = 320
    COLOR_HEIGHT: Final = 240


class LcdMode(Enum):
    """LCD Mode."""
    NONE: Final = '0'
    BLACK_WHITE: Final = '1'
    TRUE_COLOR: Final = 'RGBA'


class FontsConfig(BaseModel):
    """Fonts configuration for LcdInfo."""
    name: str
    small: int
    medium: int
    large: int


class LcdInfo(BaseModel):
    """LCD info."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    width: LcdSize
    height: LcdSize
    type: LcdType
    foreground: Union[int, tuple[int, int, int, int]]
    background: Union[int, tuple[int, int, int, int]]
    mode: LcdMode
    line_spacing: int
    font_xs: Optional[ImageFont.FreeTypeFont] = None
    font_s: Optional[ImageFont.FreeTypeFont] = None
    font_l: Optional[ImageFont.FreeTypeFont] = None

    def set_fonts(self, fonts: FontsConfig) -> None:
        """
        Set fonts configuration.

        :param fonts: fonts configuration
        """
        self.font_xs = ImageFont.truetype(fonts.name, fonts.small)
        self.font_s = ImageFont.truetype(fonts.name, fonts.medium)
        self.font_l = ImageFont.truetype(fonts.name, fonts.large)

    def __str__(self) -> str:
        return f'{self.type.name.capitalize()} LCD: {self.width.value}x{self.height.value} px'


NoneLcd = LcdInfo(width=LcdSize.NONE, height=LcdSize.NONE, type=LcdType.NONE, line_spacing=0,
                  foreground=0, background=0, mode=LcdMode.NONE)
LcdMono = LcdInfo(width=LcdSize.MONO_WIDTH, height=LcdSize.MONO_HEIGHT, type=LcdType.MONO, line_spacing=10,
                  foreground=255, background=0, mode=LcdMode.BLACK_WHITE)
LcdColor = LcdInfo(width=LcdSize.COLOR_WIDTH, height=LcdSize.COLOR_HEIGHT, type=LcdType.COLOR, line_spacing=40,
                   foreground=(0, 255, 0, 255), background=(0, 0, 0, 0), mode=LcdMode.TRUE_COLOR)


class Gkey(BaseModel):
    """Logitech G-Key."""
    key: int
    mode: int

    def __str__(self) -> str:
        """Return with format G<i>/M<j>."""
        return f'G{self.key}_M{self.mode}'

    def __bool__(self) -> bool:
        """Return False when any of value is zero."""
        return all([self.key, self.mode])

    def __hash__(self) -> int:
        """Hash will be the same for any two Gkey instances with the same key and mode values."""
        return hash((self.key, self.mode))

    @classmethod
    def from_yaml(cls, /, yaml_str: str) -> 'Gkey':
        """
        Construct Gkey from YAML string.

        :param yaml_str: G-Key string, example: G2_M1
        :return: Gkey instance
        """
        match = search(r'G(\d+)_M(\d+)', yaml_str)
        if match:
            return cls(**{k: int(i) for k, i in zip(('key', 'mode'), match.groups())})
        raise ValueError(f'Invalid Gkey format: {yaml_str}. Expected: G<i>_M<j>')

    @staticmethod
    def generate(key: int, mode: int) -> Sequence['Gkey']:
        """
        Generate a sequence of G-Keys.

        :param key: Number of keys
        :param mode: Number of modes
        :return:
        """
        return tuple([Gkey(key=k, mode=m) for k in range(1, key + 1) for m in range(1, mode + 1)])


class DeviceRowsNumber(BaseModel):
    """Represent the number of rows for different types of devices."""
    g_key: int = 0
    lcd_key: int = 0
    mouse_key: int = 0

    @property
    def total(self) -> int:
        """
        Get the total number of rows.

        :return: The total count of rows as an integer.
        """
        return sum([self.g_key, self.lcd_key, self.mouse_key])


class LogitechDeviceModel(BaseModel):
    """
    Logitech Device model.

    It describes all capabilities of any Logitech device.
    """
    klass: str
    no_g_modes: int = 0
    no_g_keys: int = 0
    btn_m_range: tuple[int, int] = (0, 0)
    lcd_keys: Sequence[LcdButton] = tuple()
    lcd_info: LcdInfo = NoneLcd

    def get_key_at(self, row: int, col: int) -> Optional[Union[LcdButton, Gkey, MouseButton]]:
        """
        Get the keys at the specified row and column in the table layout.

        :param row: The row index, zero based.
        :param col: The column index, zero based.
        :return: The key at the specified row and column, if it exists, otherwise None.
        """
        try:
            g_keys = [[Gkey(key=r, mode=c) for c in range(1, self.no_g_modes + 1)] for r in range(1, self.no_g_keys + 1)]
            lcd_buttons = []
            mouse_buttons = []

            if self.lcd_keys:
                lcd_buttons = [[lcd_key] + [None] * (self.no_g_modes - 1) for lcd_key in self.lcd_keys]
            if len(self.mouse_keys) > 1:
                mouse_buttons = [[mouse_key] + [None] * (self.no_g_modes - 1) for mouse_key in self.mouse_keys]

            table_layout = g_keys + lcd_buttons + mouse_buttons
            return table_layout[row][col]
        except IndexError:
            return None

    @property
    def rows(self) -> DeviceRowsNumber:
        """
        Get the number of rows for each key category.

        :return: A DeviceRowsNumber with the number of rows for each category.
        """
        return DeviceRowsNumber(
            g_key=self.no_g_keys,
            lcd_key=len(self.lcd_keys),
            mouse_key=0 if len(self.mouse_keys) == 1 else len(self.mouse_keys)
        )

    @property
    def cols(self) -> int:
        """
        Get the number of columns required.

        :return: The number of columns required.
        """
        mouse_btn_exist = 1 if self.btn_m_range != (0, 0) else 0
        lcd_btn_exists = 1 if self.lcd_keys else 0
        return max([self.no_g_modes, mouse_btn_exist, lcd_btn_exists])

    def __str__(self) -> str:
        result = []
        if self.lcd_info.type.value:
            result.append(f'{self.lcd_info}')
        if self.lcd_keys:
            lcd_buttons = ', '.join([str(lcd_btn) for lcd_btn in self.lcd_keys])
            result.append(f'LCD Buttons: {lcd_buttons}')
        if self.no_g_modes and self.no_g_keys:
            result.append(f'G-Keys: {self.no_g_keys} in {self.no_g_modes} modes')
        if self.btn_m_range[0] and self.btn_m_range[1]:
            result.append(f'Mouse Buttons: {self.btn_m_range[0]} to {self.btn_m_range[1]}')
        return '\n'.join(result)

    @property
    def g_keys(self) -> Sequence[Gkey]:
        """
        Generate a sequence of G-Keys.

        :return: A sequence of G-Keys.
        """
        return Gkey.generate(key=self.no_g_keys, mode=self.no_g_modes)

    @property
    def mouse_keys(self) -> Sequence[MouseButton]:
        """
        Generate a sequence of MouseButtons.

        :return: A sequence of MouseButtons.
        """
        return MouseButton.generate(button_range=self.btn_m_range)

    @property
    def lcd_name(self) -> str:
        """
        Get the LCD name in lower case.

        :return: The name of the LCD as a lowercase string.
        """
        return self.lcd_info.type.name.lower()


G19 = LogitechDeviceModel(klass='G19', no_g_modes=3, no_g_keys=12, lcd_info=LcdColor,
                          lcd_keys=(LcdButton.LEFT, LcdButton.RIGHT, LcdButton.OK, LcdButton.CANCEL, LcdButton.UP, LcdButton.DOWN, LcdButton.MENU))
G13 = LogitechDeviceModel(klass='G13', no_g_modes=3, no_g_keys=29, lcd_info=LcdMono,
                          lcd_keys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))
G15v1 = LogitechDeviceModel(klass='G15v1', no_g_modes=3, no_g_keys=18, lcd_info=LcdMono,
                            lcd_keys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))
G15v2 = LogitechDeviceModel(klass='G15v2', no_g_modes=3, no_g_keys=6, lcd_info=LcdMono,
                            lcd_keys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))
G510 = LogitechDeviceModel(klass='G510', no_g_modes=3, no_g_keys=18, lcd_info=LcdMono,
                           lcd_keys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))
LCD_KEYBOARDS_DEV = [G19, G510, G15v1, G15v2, G13]

G910 = LogitechDeviceModel(klass='G910', no_g_modes=3, no_g_keys=9)
G710 = LogitechDeviceModel(klass='G710', no_g_modes=3, no_g_keys=6)
G110 = LogitechDeviceModel(klass='G110', no_g_modes=3, no_g_keys=12)
G103 = LogitechDeviceModel(klass='G103', no_g_modes=3, no_g_keys=6)
G105 = LogitechDeviceModel(klass='G105', no_g_modes=3, no_g_keys=6)
G11 = LogitechDeviceModel(klass='G11', no_g_modes=3, no_g_keys=18)
KEYBOARDS_DEV = [G910, G710, G110, G103, G105, G11]

G35 = LogitechDeviceModel(klass='G35', no_g_modes=1, no_g_keys=3)
G633 = LogitechDeviceModel(klass='G633', no_g_modes=1, no_g_keys=3)
G930 = LogitechDeviceModel(klass='G930', no_g_modes=1, no_g_keys=3)
G933 = LogitechDeviceModel(klass='G933', no_g_modes=1, no_g_keys=3)
HEADPHONES_DEV = [G35, G633, G930, G933]

G600 = LogitechDeviceModel(klass='G600', btn_m_range=(6, 20))
G300 = LogitechDeviceModel(klass='G300', btn_m_range=(6, 9))
G400 = LogitechDeviceModel(klass='G400', btn_m_range=(6, 8))
G700 = LogitechDeviceModel(klass='G700', btn_m_range=(1, 13))
G9 = LogitechDeviceModel(klass='G9', btn_m_range=(4, 8))
MX518 = LogitechDeviceModel(klass='MX518', btn_m_range=(6, 8))
G402 = LogitechDeviceModel(klass='G402', btn_m_range=(1, 5))
G502 = LogitechDeviceModel(klass='G502', btn_m_range=(4, 8))
G602 = LogitechDeviceModel(klass='G602', btn_m_range=(6, 10))
MOUSES_DEV = [G600, G300, G400, G700, G9, MX518, G402, G502, G602]

ALL_DEV = LCD_KEYBOARDS_DEV + KEYBOARDS_DEV + HEADPHONES_DEV + MOUSES_DEV


def _try_key_instance(klass: Union[type[Gkey], type[LcdButton], type[MouseButton]], method: str, key_str: str) -> Optional[Union[LcdButton, Gkey, MouseButton]]:
    """
    Detect key string could be parsed with method.

    :param klass: Class of the key instance to try the method on
    :param method: Name of the method to try with the key class.
    :param key_str: A string representation of the key
    :return: The result of calling the method on the key instance, or None if an error occurs.

    """
    try:
        return getattr(klass, method)(key_str)
    except TypeError:
        return getattr(klass, method)
    except (ValueError, AttributeError):
        return None


def get_key_instance(key_str: str) -> Union[LcdButton, Gkey, MouseButton]:
    """
    Get key instance from string.

    :param key_str: Key name from yaml configuration
    :return: LcdButton, Gkey or MouseButton instance
    """
    for klass, method in [(Gkey, 'from_yaml'), (MouseButton, 'from_yaml'), (LcdButton, key_str)]:
        key_instance = _try_key_instance(klass=klass, method=method, key_str=key_str)
        if key_instance:
            return key_instance
    raise AttributeError(f'Could not resolve "{key_str}" to a Gkey/LcdButton/MouseButton instance')


class MsgBoxTypes(Enum):
    """Message box types."""
    INFO = 'information'
    QUESTION = 'question'
    WARNING = 'warning'
    CRITICAL = 'critical'
    ABOUT = 'about'
    ABOUT_QT = 'aboutQt'


class SystemData(BaseModel):
    """Stores system related information."""
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

    @property
    def sha(self) -> str:
        """Get SHA from DCS_BIOS repo."""
        return self.dcs_bios_ver.split(' ')[0]


DcspyConfigYaml = dict[str, Union[str, int, bool]]


class Direction(Enum):
    """Direction of iteration."""
    FORWARD = 1
    BACKWARD = -1


class ZigZagIterator:
    """Iterate with values from zero (0) to max_val and back."""
    def __init__(self, current: int, max_val: int, step: int = 1) -> None:
        """
        Initialize with current and max value.

        Default direction is towards max_val.

        :param current: current value
        :param max_val: maximum value
        :param step: step size, 1 by default
        """
        self.current = current
        self.step = step
        self.max_val = max_val
        self._direction = Direction.FORWARD

    def __iter__(self) -> 'ZigZagIterator':
        return self

    def __str__(self) -> str:
        return f'current: {self.current} step: {self.step} max value: {self.max_val}'

    def __next__(self) -> int:
        if self.current >= self.max_val:
            self._direction = Direction.BACKWARD
        elif self.current <= 0:
            self._direction = Direction.FORWARD
        self.current += self.step * self._direction.value
        if self._direction == Direction.FORWARD:
            self.current = min(self.current, self.max_val)
        else:
            self.current = max(0, self.current)
        return self.current

    @property
    def direction(self) -> Direction:
        """Return direction."""
        return self._direction

    @direction.setter
    def direction(self, value: Direction) -> None:
        """
        Set direction.

        :param value: `Direction.FORWARD` or `Direction.BACKWARD`
        """
        self._direction = value


class ReleaseInfo(BaseModel):
    """Store release related information."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    latest: bool
    ver: version.Version
    dl_url: str
    published: str
    release_type: str
    asset_file: str


class RequestType(Enum):
    """Internal request types."""
    CYCLE = 'CYCLE'
    CUSTOM = 'CUSTOM'
    PUSH_BUTTON = 'PUSH_BUTTON'


class RequestModel(BaseModel):
    """Abstract request representation with common interface to send requests via UDE socket."""

    ctrl_name: str
    raw_request: str
    get_bios_fn: Callable[[str], Union[str, int, float]]
    cycle: CycleButton = CycleButton(ctrl_name='', step=0, max_value=0)
    key: Union[LcdButton, Gkey, MouseButton]

    @field_validator('ctrl_name')
    def validate_interface(cls, value: str) -> str:
        """
        Validate.

        :param value:
        :return:
        """
        if not value or not all(ch.isupper() or ch == '_' or ch.isdigit() for ch in value):
            raise ValueError("Invalid value for 'ctrl_name'. Only A-Z, 0-9 and _ are allowed.")
        return value

    @classmethod
    def from_request(cls, key: Union[LcdButton, Gkey, MouseButton], request: str, get_bios_fn: Callable[[str], Union[str, int, float]]) -> 'RequestModel':
        """
        Build an object based on string request.

        For cycle request `get_bios_fn` is used to update a current value of BIOS selector.

        :param key: LcdButton, Gkey or MouseButton
        :param request: The raw request string.
        :param get_bios_fn: A callable function that returns a current value for BIOS selector.
        :return: An instance of the RequestModel class.
        """
        cycle_button = CycleButton(ctrl_name='', step=0, max_value=0)
        if RequestType.CYCLE.value in request:
            cycle_button = CycleButton.from_request(request)
        ctrl_name = request.split(' ')[0]
        return RequestModel(ctrl_name=ctrl_name, raw_request=request, get_bios_fn=get_bios_fn, cycle=cycle_button, key=key)

    @classmethod
    def empty(cls, key: Union[LcdButton, Gkey, MouseButton]) -> 'RequestModel':
        """
        Create an empty request model, for a key which isn't assign.

        :param key: LcdButton, Gkey or MouseButton
        :return: The created request model.
        """
        return RequestModel(ctrl_name='EMPTY', raw_request='', get_bios_fn=int, cycle=CycleButton(ctrl_name='', step=0, max_value=0), key=key)

    def _get_next_value_for_button(self) -> int:
        """Get next an integer value (cycle fore and back) for ctrl_name BIOS selector."""
        if not isinstance(self.cycle.iter, ZigZagIterator):
            self.cycle.iter = ZigZagIterator(current=int(self.get_bios_fn(self.ctrl_name)),
                                             step=self.cycle.step,
                                             max_val=self.cycle.max_value)
        return next(self.cycle.iter)

    @property
    def is_cycle(self) -> bool:
        """Return True if cycle request, False otherwise."""
        return bool(self.cycle)

    @property
    def is_custom(self) -> bool:
        """Return True if custom request, False otherwise."""
        return RequestType.CUSTOM.value in self.raw_request

    @property
    def is_push_button(self) -> bool:
        """Return True if push button request, False otherwise."""
        return RequestType.PUSH_BUTTON.value in self.raw_request

    def bytes_requests(self, key_down: Optional[int] = None) -> list[bytes]:
        """
        Generate a list of bytes that represent the individual requests based on the current state of the model.

        :param key_down: One (1) indicates when G-Key was pushed down and zero (0) when G-Key is up
        :return: a list of bytes representing the individual requests
        """
        request = self._generate_request_based_on_case(key_down)
        return [bytes(req, 'utf-8') for req in request.split('|')]

    def _generate_request_based_on_case(self, key_down: Optional[int] = None) -> str:
        """
        Generate a request based on the current state of the object.

        The request is determined by a set of conditions defined in the `request_mapper` dictionary.
        Each condition is associated with a method that generates the request for that condition.

        :param key_down: One (1) indicates when G-Key was pushed down and zero (0) when G-Key is up
        :return: A string representing the generated request based on the given conditions and parameters.
        """
        class CaseDict(TypedDict):
            condition: bool
            method: partial
        request_mapper: dict[int, CaseDict] = {
            1: {'condition': self.is_push_button and isinstance(self.key, Gkey),
                'method': partial(self.__generate_push_btn_req_for_gkey_and_mouse, key_down)},
            2: {'condition': self.is_push_button and isinstance(self.key, MouseButton),
                'method': partial(self.__generate_push_btn_req_for_gkey_and_mouse, key_down)},
            3: {'condition': self.is_push_button and isinstance(self.key, LcdButton),
                'method': partial(self.__generate_push_btn_req_for_lcd_button)},
            4: {'condition': key_down is None or key_down == KEY_UP,
                'method': partial(RequestModel.__generate_empty)},
            5: {'condition': self.is_cycle,
                'method': partial(self.__generate_cycle_request)},
            6: {'condition': self.is_custom,
                'method': partial(self.__generate_custom_request)},
        }

        for case in request_mapper.values():
            if case['condition']:
                return case['method']()
        return f'{self.raw_request}\n'

    def __generate_push_btn_req_for_gkey_and_mouse(self, key_down: Optional[int]) -> str:
        """
        Generate a push button request for GKey and MouseButton.

        :param key_down: Optional integer representing the key pressed down.
        """
        return f'{self.ctrl_name} {key_down}\n'

    def __generate_push_btn_req_for_lcd_button(self) -> str:
        """Generate the push button request for the LCD button."""
        return f'{self.ctrl_name} {KEY_DOWN}\n|{self.ctrl_name} {KEY_UP}\n'

    @staticmethod
    def __generate_empty() -> str:
        """Generate an empty string."""
        return ''

    def __generate_cycle_request(self) -> str:
        """Generate a cycle request."""
        return f'{self.ctrl_name} {self._get_next_value_for_button()}\n'

    def __generate_custom_request(self) -> str:
        """Generate a custom request from the raw request."""
        request = self.raw_request.split(f'{RequestType.CUSTOM.value} ')[1]
        request = request.replace('|', '\n|')
        return request.strip('|')

    def __str__(self) -> str:
        return f'{self.ctrl_name}: {self.raw_request}'

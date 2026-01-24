from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
from ctypes import c_void_p
from datetime import datetime
from enum import Enum, IntEnum
from functools import partial
from os import environ
from pathlib import Path
from platform import architecture
from re import search
from sys import maxsize
from tempfile import gettempdir
from typing import Any, Final, TypedDict, TypeVar, Union

from _ctypes import sizeof
from packaging import version
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, ConfigDict, RootModel, field_validator

__version__ = '3.8.0'

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
BIOS_REPO_NAME: Final = 'DCS-Skunkworks/dcs-bios'
BIOS_REPO_ADDR: Final = f'https://github.com/{BIOS_REPO_NAME}.git'
DEFAULT_FONT_NAME: Final = 'consola.ttf'
CTRL_LIST_SEPARATOR: Final = '--'
CONFIG_YAML: Final = 'config.yaml'
DEFAULT_YAML_FILE: Final = Path(__file__).parent / 'resources' / CONFIG_YAML
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
    'C130J30': {'name': 'C-130J 30 Hercules', 'bios': 'C-130J-30'},
}

BiosValue = Union[str, int, float]


class AircraftKwargs(TypedDict):
    """Represent the keyword arguments expected by the Aircraft class."""
    update_display: Callable[[Image.Image], None]
    bios_data: Mapping[str, BiosValue]


class ApacheDrawModeKwargs(TypedDict):
    """Keyword arguments for Apache draw mode."""
    draw: ImageDraw.ImageDraw


class ApacheAllDrawModesKwargs(ApacheDrawModeKwargs, total=False):
    """Keyword arguments for Apache all draw modes."""
    scale: int | None
    x_cords: list[int] | None
    y_cords: list[int] | None
    font: ImageFont.FreeTypeFont | None


class ApacheEufdMode(Enum):
    """Apache EUFD Mode."""
    IDM = 'idm'
    WCA = 'wca'
    PRE = 'pre'


class Input(BaseModel):
    """Input base class of inputs section of Control."""
    description: str

    def get(self, attribute: str, default=None) -> Any | None:
        """
        Access an attribute and get default when is not available.

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
    """VariableStep input interface of the inputs section of Control."""
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
    """SetState input interface of the inputs section of Control."""
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
    """Action input interface of the inputs section of Control."""
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


Inputs = Union[FixedStep, VariableStep, SetState, Action, SetString]


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
    """Integer output interface of the outputs section of Control."""
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
    value: int
    max_value: int


class StrBuffArgs(BaseModel):
    """Arguments of BIOS String Buffer."""
    address: int
    max_length: int


class BiosValueStr(BaseModel):
    """Value of BIOS String Buffer."""
    klass: str
    args: StrBuffArgs
    value: str


class ControlDepiction(BaseModel):
    """Represent the depiction of a control."""
    name: str
    description: str


class ControlKeyData:
    """Describes input data for cockpit controller."""

    def __init__(self, name: str, description: str, max_value: int, suggested_step: int = 1) -> None:
        """
        Define a type of input for a cockpit controller.

        :param name: Name of the input
        :param description: Short description
        :param max_value: Max value (zero-based)
        :param suggested_step: One (1) by default
        """
        self.name = name
        self.description = description
        self.max_value = max_value
        self.suggested_step = suggested_step
        self.list_dict: list[Inputs] = []

    def __repr__(self) -> str:
        return f'KeyControl({self.name}: {self.description} - max_value={self.max_value}, suggested_step={self.suggested_step}'

    def __bool__(self) -> bool:
        """Return True if both `max_value` and `suggested_step`: are truthy, False otherwise."""
        if not all([self.max_value, self.suggested_step]):
            return False
        return True

    @classmethod
    def from_control(cls, /, ctrl: Control) -> ControlKeyData:
        """
        Construct an object based on Control BIOS Model.

        :param ctrl: Control BIOS model
        :return: ControlKeyData instance
        """
        try:
            max_value = cls._get_max_value(ctrl.inputs)
            suggested_step: int = max(d.get('suggested_step', 1) for d in ctrl.inputs)  # type: ignore[type-var, assignment]
        except ValueError:
            max_value = 0
            suggested_step = 0
        instance = cls(name=ctrl.identifier, description=ctrl.description, max_value=max_value, suggested_step=suggested_step)
        instance.list_dict = ctrl.inputs
        return instance

    @staticmethod
    def _get_max_value(list_of_dicts: list[Inputs]) -> int:
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
    def __get_max(list_of_dicts: list[Inputs]) -> tuple[int, bool]:
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

        :return: ControlDepiction object representing the control's name and description.
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
        Check if an input has only one input dict.

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

        :return: True if a controller is a push button type, False otherwise
        """
        return self.has_fixed_step and self.has_set_state and self.max_value == 1


class Control(BaseModel):
    """Control section of the BIOS model."""
    api_variant: str | None = None
    category: str
    control_type: str
    description: str
    identifier: str
    inputs: list[FixedStep | VariableStep | SetState | Action | SetString]
    outputs: list[OutputStr | OutputInt]

    @property
    def input(self) -> ControlKeyData:
        """
        Extract inputs data.

        :return: ControlKeyData
        """
        return ControlKeyData.from_control(ctrl=self)

    @property
    def output(self) -> BiosValueInt | BiosValueStr:
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

    @classmethod
    def make_empty(cls) -> Control:
        """
        Make an empty Control object with default values assigned to its attributes.

        :return: Control an object with empty values.
        """
        return cls(api_variant='', category='', control_type='', description='', identifier='', inputs=[], outputs=[])

    def __bool__(self) -> bool:
        """Return True if all attributes: are truthy, False otherwise."""
        return all([self.api_variant, self.category, self.control_type, self.description, self.identifier, len(self.inputs), len(self.outputs)])


class DcsBiosPlaneData(RootModel):
    """DcsBios plane data model."""
    root: dict[str, dict[str, Control]]

    def get_ctrl(self, ctrl_name: str) -> Control:
        """
        Get Control from DCS-BIOS with name.

        :param ctrl_name: Control name
        :return: Control instance
        """
        for controllers in self.root.values():
            for ctrl, data in controllers.items():
                if ctrl == ctrl_name:
                    return Control.model_validate(data)
        return Control.make_empty()

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
    """Map BIOS key string with iterator to keep a current value."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ctrl_name: str
    step: int = 1
    max_value: int = 1
    iter: Iterator[int] = iter([0])

    @classmethod
    def from_request(cls, /, req: str) -> CycleButton:
        """
        Convert a request string to a `CycleButton` instance by extracting the necessary details from the request's components.

        The request is expected to follow a predefined structure where its components
        are separated by spaces.

        :param req: A string a request expected to contain `control_name`, an underscore, `step`, and `max_value`, separated by spaces.
        :return: Instance of `CycleButton` based on extracted data.
        """
        selector, _, step, max_value = req.split(' ')
        return CycleButton(ctrl_name=selector, step=int(step), max_value=int(max_value))

    def __bool__(self) -> bool:
        """Return True if any of the attributes: `step`, `max_value`, `ctrl_name` is truthy, False otherwise."""
        return not all([not self.step, not self.max_value, not self.ctrl_name])


class GuiPlaneInputRequest(BaseModel):
    """
    Represents a GUI plane input request.

    This class is used to construct and manage input requests originating from
    a graphical interface, such as radio buttons or other control widgets,
    that interact with plane systems.
    It allows for structured generation of requests based on provided parameters or
    configurations and provides utility methods to convert data into request objects.
    """
    identifier: str
    request: str
    widget_iface: str

    @classmethod
    def from_control_key(cls, ctrl_key: ControlKeyData, rb_iface: str, custom_value: str = '') -> GuiPlaneInputRequest:
        """
        Create an instance of GuiPlaneInputRequest based on provided control key data, a request type and optional custom value.

        The method generates a request string for the GUI widget interface determined by the specified request type (rb_iface)
        using information from the ControlKeyData object (ctrl_key).
        If a custom value is provided, it incorporates the value into the generated request for certain request types.

        :param ctrl_key: A ControlKeyData is an object used to specify the control key's attributes, such as its name, suggested step, and maximum value.
        :param rb_iface: A string that represents the requested widget interface type, options include types such as 'rb_action', 'rb_fixed_step_inc', etc.
        :param custom_value: An optional string used to provide a custom value for specific request types ('rb_custom' or 'rb_set_state').
        :return: A GuiPlaneInputRequest object initialized with the identifier, generated request string and the specified widget interface type.
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
    def from_plane_gkeys(cls, /, plane_gkeys: dict[str, str]) -> dict[str, GuiPlaneInputRequest]:
        """
        Create a dictionary mapping unique plane keys to `GuiPlaneInputRequest` objects, based on input configuration data.

        The method processes each key-value pair where the value contains a request type and determines the appropriate widget
        interface based on specified keywords.
        A mapping dictionary is used to identify widget interfaces corresponding to request types.

        :param plane_gkeys: A dictionary where each key is a plane identifier (string) and the value is
                            a space-separated string of configuration data that includes a request type.
        :return: A dictionary mapping each plane identifier (string) to a `GuiPlaneInputRequest` instance.
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
    def make_empty(cls) -> GuiPlaneInputRequest:
        """
        Create an empty GuiPlaneInputRequest object with default values assigned to its attributes.

        :return: An instance of GuiPlaneInputRequest with default empty values
        """
        return cls(identifier='', request='', widget_iface='')


class LedConstants(Enum):
    """LED constants."""
    LOGI_LED_DURATION_INFINITE = 0
    LOGI_DEVICETYPE_MONOCHROME = 1
    LOGI_DEVICETYPE_RGB = 2
    LOGI_DEVICETYPE_ALL = 3  # LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB


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

    def __str__(self) -> str:
        return self.name


class MouseButton(BaseModel):
    """
    Representation of a mouse button.

    Provides functionality for working with mouse buttons, including conversion
    to string, boolean evaluation, hashing and constructing instances from YAML
    strings.
    Supports generating sequences of mouse buttons within a specified range.
    """
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
    def from_yaml(cls, /, yaml_str: str) -> MouseButton:
        """
        Create a MouseButton object from a YAML string representation.

        This method parses a given YAML string to extract the button number
        encoded in the format `M_<i>` (such as `M_1`, `M_2`, etc.) and generates
        a MouseButton instance for the corresponding button.
        If the format does not conform to expectations and parsing fails, a ValueError is raised.

        :param yaml_str: The YAML string representing the mouse button in the format `M_<i>`.
        :return: A MouseButton instance derived from the specified YAML string.
        :raises ValueError: If the provided YAML string does not match the expected format `M_<i>`.
        """
        match = search(r'M_(\d+)', yaml_str)
        if match:
            return cls(button=int(match.group(1)))
        raise ValueError(f'Invalid MouseButton format: {yaml_str}. Expected: M_<i>')

    @staticmethod
    def generate(button_range: tuple[int, int]) -> Sequence[MouseButton]:
        """
        Generate a sequence of MouseButton objects based on the provided range.

        This utility creates MouseButton instances for each integer value within
        the inclusive range defined by the ``button_range`` tuple.

        :param button_range: A tuple of two integers, representing the start and end of the range (inclusive) for generating MouseButton objects.
        :return: A tuple containing instantiated MouseButton objects for each value in the specified range.
        """
        return tuple(MouseButton(button=m) for m in range(button_range[0], button_range[1] + 1))


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
    def from_yaml(cls, /, yaml_str: str) -> Gkey:
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
    def generate(key: int, mode: int) -> Sequence[Gkey]:
        """
        Generate a sequence of G-Keys.

        :param key: Number of keys
        :param mode: Number of modes
        :return: sequence of Gkey instances
        """
        return tuple(Gkey(key=k, mode=m) for k in range(1, key + 1) for m in range(1, mode + 1))


AnyButton = Union[LcdButton, Gkey, MouseButton]


class LcdType(Enum):
    """LCD Type."""
    NONE = 0
    MONO = 1
    COLOR = 2


class LcdSize(Enum):
    """LCD dimensions."""
    NONE = 0
    MONO_WIDTH = 160
    MONO_HEIGHT = 43
    COLOR_WIDTH = 320
    COLOR_HEIGHT = 240


class LcdMode(Enum):
    """LCD Mode."""
    NONE = '0'
    BLACK_WHITE = '1'
    TRUE_COLOR = 'RGBA'


class FontsConfig(BaseModel):
    """Fonts configuration for LcdInfo."""
    name: str
    small: int
    medium: int
    large: int
    ded_font: bool = False


class LcdInfo(BaseModel):
    """LCD info."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    width: LcdSize
    height: LcdSize
    type: LcdType
    foreground: int | tuple[int, int, int, int]
    background: int | tuple[int, int, int, int]
    mode: LcdMode
    line_spacing: int
    font_xs: ImageFont.FreeTypeFont | None = None
    font_s: ImageFont.FreeTypeFont | None = None
    font_l: ImageFont.FreeTypeFont | None = None
    font_ded: ImageFont.FreeTypeFont | None = None

    def set_fonts(self, fonts: FontsConfig) -> None:
        """
        Set fonts configuration.

        :param fonts: fonts configuration
        """
        self.font_xs = ImageFont.truetype(fonts.name, fonts.small)
        self.font_s = ImageFont.truetype(fonts.name, fonts.medium)
        self.font_l = ImageFont.truetype(fonts.name, fonts.large)
        self.font_ded = None
        if fonts.ded_font:
            path_falcon_ded = Path(__file__) / '..' / 'resources' / 'falconded.ttf'
            self.font_ded = ImageFont.truetype(str(path_falcon_ded.resolve()), 25)

    def __str__(self) -> str:
        return f'{self.type.name.capitalize()} LCD: {self.width.value}x{self.height.value} px'


NoneLcd = LcdInfo(width=LcdSize.NONE, height=LcdSize.NONE, type=LcdType.NONE, line_spacing=0,
                  foreground=0, background=0, mode=LcdMode.NONE)
LcdMono = LcdInfo(width=LcdSize.MONO_WIDTH, height=LcdSize.MONO_HEIGHT, type=LcdType.MONO, line_spacing=10,
                  foreground=255, background=0, mode=LcdMode.BLACK_WHITE)
LcdColor = LcdInfo(width=LcdSize.COLOR_WIDTH, height=LcdSize.COLOR_HEIGHT, type=LcdType.COLOR, line_spacing=40,
                   foreground=(0, 255, 0, 255), background=(0, 0, 0, 0), mode=LcdMode.TRUE_COLOR)


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
    lcd_keys: Sequence[LcdButton] = ()
    lcd_info: LcdInfo = NoneLcd

    def get_key_at(self, row: int, col: int) -> AnyButton | None:
        """
        Get the keys at the specified row and column in the table layout.

        :param row: The row index (zero-based).
        :param col: The column index (zero-based).
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


class MsgBoxTypes(Enum):
    """Message box types."""
    INFO = 'information'
    QUESTION = 'question'
    WARNING = 'warning'
    CRITICAL = 'critical'
    ABOUT = 'about'
    ABOUT_QT = 'aboutQt'


class SystemData(BaseModel):
    """Stores system and application-related information."""
    system: str
    release: str
    ver: str
    proc: str
    dcs_ver: str
    dcspy_ver: str
    bios_ver: str
    dcs_bios_ver: str
    git_ver: str

    @property
    def sha(self) -> str:
        """
        Provides a property to retrieve the SHA part of the DCS-BIOS repo.

        :return: The extracted SHA value from the `dcs_bios_ver` string.
        """
        return self.dcs_bios_ver.split(' ')[0]


ConfigValue = TypeVar('ConfigValue', str, int, float, bool)
DcspyConfigYaml = dict[str, ConfigValue]


class Direction(IntEnum):
    """Direction of iteration."""
    FORWARD = 1
    BACKWARD = -1


class ZigZagIterator:
    """
    An iterator that moves within a range in an oscillating pattern.

    The iterator starts at a given current value, progresses or retreats based on the defined step size
    and changes a direction upon reaching the boundaries of the range (`max_val` and 0).
    This allows for oscillating behavior within the specified limits.
    The class also provides access to its current direction of iteration.
    """
    def __init__(self, current: int, max_val: int, step: int = 1) -> None:
        """
        Represent a simple iterator with a defined range and step increment.

        The iterator maintains a current value, a maximum limit, and adjusts
        its progression based on the specified step.
        It also tracks the direction of iteration internally.

        :param current: The starting point of the iterator.
        :param max_val: The upper limit of the iterator range.
        :param step: The increment value for each iteration, defaults to 1.
        """
        self.current = current
        self.step = step
        self.max_val = max_val
        self._direction = Direction.FORWARD

    def __iter__(self) -> ZigZagIterator:
        return self

    def __str__(self) -> str:
        return f'current: {self.current} step: {self.step} max value: {self.max_val}'

    def __next__(self) -> int:
        if self.current >= self.max_val:
            self._direction = Direction.BACKWARD
        elif self.current <= 0:
            self._direction = Direction.FORWARD
        self.current += self.step * self._direction
        if self._direction == Direction.FORWARD:
            self.current = min(self.current, self.max_val)
        else:
            self.current = max(0, self.current)
        return self.current

    @property
    def direction(self) -> Direction:
        """
        Represent the direction of an iterator or entity within a defined context.

        This property retrieves the current direction of the iterator.

        :return: The current direction of the iterator.
        """
        return self._direction

    @direction.setter
    def direction(self, value: Direction) -> None:
        """
        Set the direction of the current instance.

        :param value: The new direction to assign to the instance.
        """
        self._direction = value


class Asset(BaseModel):
    """
    Representation of an asset with metadata information.

    This class is used to encapsulate details about an asset such as its
    URL, name, label, content type, size and download location.
    It also provides functionality to validate the asset's properties against specific criteria.
    """
    url: str
    name: str
    label: str
    content_type: str
    size: int
    browser_download_url: str

    def get_asset_with_name(self, extension: str = '', file_name: str = '') -> Asset | None:
        """
        Retrieve the asset if its name matches the specified file extension and contains the given file name.

        This method checks if the name of the asset ends with the provided file extension and if the given file name is a substring of the asset's name.

        :param extension: The file extension to check for.
        :param file_name: The specific file name to look for within the asset's name.
        :return: The Asset instance if the name matches, otherwise None.
        """
        if self.name.endswith(extension) and file_name in self.name:
            return self
        return None


class Release(BaseModel):
    """
    Representation of a software release.

    The Release class provides detailed information about a specific release of a software project,
    including metadata such as URLs, tags, names, and dates.
    It also includes functionality to determine whether a release is the latest and to
    retrieve downloadable assets.
    """
    url: str
    html_url: str
    tag_name: str
    name: str
    draft: bool
    prerelease: bool
    created_at: str
    published_at: str
    assets: list[Asset]
    body: str

    def is_latest(self, current_ver: str | version.Version) -> bool:
        """
        Determine if the provided version is the latest compared to the instance's version.

        This method compares the version of the current object with a given version to check
        if the current version is equal to or earlier than the given version.

        :param current_ver: The version to compare against, it can be provided as a string or as a version.Version object.
        :return: Returns True if the current version is less than or equal to the provided version (indicating it is the latest), False otherwise.
        """
        if isinstance(current_ver, str):
            current_ver = version.parse(current_ver)
        return self.version <= current_ver

    def get_asset(self, extension: str = '', file_name: str = '') -> Asset | None:
        """
        Retrieve the asset if its name matches the specified file extension and contains the given file name.

        This method checks if the name of the asset ends with the provided file extension and if the given file name is a substring of the asset's name.

        :param extension: The file extension to check for.
        :param file_name: The specific file name to look for within the asset's name.
        :return: The Asset instance if the name matches, otherwise None.
        """
        try:
            asset = next(asset for asset in self.assets if asset.get_asset_with_name(extension=extension, file_name=file_name) is not None)
        except StopIteration:
            asset = None
        return asset

    def download_url(self, extension: str = '', file_name: str = '') -> str:
        """
        Download the URL of a specific asset that matches the given file name and extension.

        This method iterates through the list of assets, applying the criteria specified by
        the `extension` and `file_name` parameters to identify the correct asset.
        If no asset matches the provided criteria, an empty string is returned.

        :param extension: The file extension to search for, defaults to an empty string if not specified.
        :param file_name: The file name to search for defaults to an empty string if not specified.
        :return: The download URL of the asset if a match is found, otherwise an empty string.
        """
        asset = self.get_asset(extension=extension, file_name=file_name)
        if asset is not None:
            return asset.browser_download_url
        return ''

    @property
    def version(self) -> version.Version:
        """
        The `version` property retrieves the software version as a `version.Version` object.

        The version data is parsed from the `tag_name` attribute, which is expected to be in a format compatible with `packaging.version`.

        :return: Parsed `Version` object representing the software version.
        """
        return version.parse(self.tag_name)

    @property
    def published(self) -> str:
        """
        Convert and format the `published_at` attribute into a human-readable date string in the format 'DD Month YYYY'.

        :return: The formatted publication date string.
        """
        published = datetime.strptime(self.published_at, '%Y-%m-%dT%H:%M:%S%z').strftime('%d %B %Y')
        return str(published)

    def verify(self, local_file: Path,
               temp_digest = Path(gettempdir()) / f'DIGESTS_{datetime.now().strftime("%Y%m%d_%H%M%S")}') -> tuple[bool, dict[str, bool]]:
        """
        Verify the integrity of a local file by comparing its checksums with the expected checksum.

        It returns True if the checksums match, indicating that the file is intact and unaltered; otherwise, it returns False.

        :param local_file: The path to the local file whose integrity is to be verified.
        :param temp_digest: Temporary file to store the digest in the local file.
        :return: True if the computed checksum matches the expected checksum, False otherwise.
        """
        from dcspy.utils import download_file, verify_hashes

        url = self.download_url(extension='', file_name='DIGESTS')
        download_file(url=url, save_path=temp_digest)
        result = verify_hashes(file_path=local_file, digest_file=temp_digest)
        return result

    def __str__(self) -> str:
        return f'{self.tag_name} pre:{self.prerelease} date:{self.published}'


class RequestType(Enum):
    """Internal request types."""
    CYCLE = 'CYCLE'
    CUSTOM = 'CUSTOM'
    PUSH_BUTTON = 'PUSH_BUTTON'


class RequestModel(BaseModel):
    """
    Represent a request model for handling different input button states and their respective BIOS actions.

    This class is designed to manage various types of input requests, including cycle, custom and push-button requests.
    It provides functionality to validate input data, generate requests in byte format, and interpret requests based on specific conditions.
    It also supports creating empty request models and handling interactions with BIOS configuration via designated callable functions.
    """
    ctrl_name: str
    raw_request: str
    get_bios_fn: Callable[[str], BiosValue]
    cycle: CycleButton = CycleButton(ctrl_name='', step=0, max_value=0)
    key: AnyButton

    @field_validator('ctrl_name')
    def validate_interface(cls, value: str) -> str:
        """
        Validate the provided interface name ensuring it consists only of uppercase letters, digits or underscores.

        This validator enforces strict naming conventions for control names, rejecting any value that contains invalid characters or is an empty string.

        :param value: The interface name to validate.
        :return: The validated interface name if it passes all checks.
        :raises ValueError: If the given value is an empty string or contains characters other than uppercase letters (A-Z), digits (0-9), or underscores (_).
        """
        if not value or not all(ch.isupper() or ch == '_' or ch.isdigit() for ch in value):
            raise ValueError("Invalid value for 'ctrl_name'. Only A-Z, 0-9 and _ are allowed.")
        return value

    @classmethod
    def from_request(cls, key: AnyButton, request: str, get_bios_fn: Callable[[str], BiosValue]) -> RequestModel:
        """
        Create an instance of the RequestModel class using a specific request string.

        This method processes the provided request string to extract necessary
        information, such as control name and cycle details.
        It initializes a CycleButton instance using the request information if applicable.
        The function then returns a RequestModel instance contains the parsed data and additional state information.

        :param key: The key representing the `AnyButton` instance tied to the request.
        :param request: The raw request string providing all request details.
        :param get_bios_fn: A callable function that retrieves BIOS values, function takes
                            a string input (BIOS key) and returns a corresponding `BiosValue` object.
        :return: A new instance of `RequestModel` contains data parsed from the provided request string and supporting parameters.
        """
        cycle_button = CycleButton(ctrl_name='', step=0, max_value=0)
        if RequestType.CYCLE.value in request:
            cycle_button = CycleButton.from_request(request)
        ctrl_name = request.split(' ')[0]
        return RequestModel(ctrl_name=ctrl_name, raw_request=request, get_bios_fn=get_bios_fn, cycle=cycle_button, key=key)

    @classmethod
    def make_empty(cls, key: AnyButton) -> RequestModel:
        """
        Create an empty instance of RequestModel with default values for its attributes.

        :param key: Represents the key parameter, which will be used as a button object type for the RequestModel instance.
        :return: A new instance of RequestModel initialized with default attribute values and the provided key parameter.
        """
        return cls(ctrl_name='EMPTY', raw_request='', get_bios_fn=int, cycle=CycleButton(ctrl_name='', step=0, max_value=0), key=key)

    def _get_next_value_for_button(self) -> int:
        """
        Determine the next value for the button using a ZigZagIterator.

        If the cycle iterator is not already an instance of ZigZagIterator, it initializes one
        using the control name and cycle attributes. Then the next value from the iterator is returned.

        :raises TypeError: If ``self.cycle.iter`` is not of the expected type and cannot be initialized properly as a ZigZagIterator instance.
        :returns: The next value as an integer generated by the ZigZagIterator.
        """
        if not isinstance(self.cycle.iter, ZigZagIterator):
            self.cycle.iter = ZigZagIterator(current=int(self.get_bios_fn(self.ctrl_name)),
                                             step=self.cycle.step,
                                             max_val=self.cycle.max_value)
        return next(self.cycle.iter)

    @property
    def is_cycle(self) -> bool:
        """
        Check if the instance has a valid cycle.

        This property checks the internal state of the instance to determine whether a valid cycle exists.
        A cycle is represented by the presence of a truthy value in the `cycle` attribute.

        :return: Returns ``True`` if a valid cycle exists, otherwise ``False``.
        """
        return bool(self.cycle)

    @property
    def is_custom(self) -> bool:
        """
        Check if the request is of type custom.

        This property evaluates whether the raw_request attribute of the object contains
        a custom request type, based on the predefined `RequestType.CUSTOM` value.

        :return: Boolean indicating if the request is of type custom.
        """
        return RequestType.CUSTOM.value in self.raw_request

    @property
    def is_push_button(self) -> bool:
        """
        Identify if the request is a push-button type.

        This property checks if the raw_request contains a specific value indicating a push-button request type
        and returns a boolean result accordingly.

        :return: True if the request is of type push-button, else False
        """
        return RequestType.PUSH_BUTTON.value in self.raw_request

    def bytes_requests(self, key_down: int | None = None) -> list[bytes]:
        """
        Generate and returns a list of byte strings based on a specific request input.

        The method generates a string request using the provided argument `key_down`.
        It then splits the generated string request using the `|` delimiter and converts each segment into a byte string.

        :param key_down: Accepts an integer representing the key value or None for default behavior.
        :return: A list containing byte strings derived from the generated request.
        """
        request = self._generate_request_based_on_case(key_down)
        return [bytes(req, 'utf-8') for req in request.split('|')]

    def _generate_request_based_on_case(self, key_down: int | None = None) -> str:
        """
        Generate a formatted request string based on various conditions and cases.

        This method evaluates different scenarios using the `request_mapper` dictionary,
        which maps integer case keys to specific conditions and methods.
        If the condition for a given case is met, the corresponding method is called to generate the request.
        If no conditions match, the raw request is returned appended with a newline.

        :param key_down: Integer representing a key state, it can be either a specific value such as `KEY_UP` or
                         `None` for cases where a key down state is not applicable.
        :return: Returns a string representing the generated request based on the active case conditions.
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

    def __generate_push_btn_req_for_gkey_and_mouse(self, key_down: int | None) -> str:
        """
        Generate a string request for handling a push-button action for both keyboard keys and mouse events.

        The function constructs a command string based on the control name and whether a key is being pressed.

        :param key_down: Either an integer value representing the key being pressed or None if no key action is specified.
        :return: A string formatted as a control name concatenated with the key_down value followed by a newline character.
        """
        return f'{self.ctrl_name} {key_down}\n'

    def __generate_push_btn_req_for_lcd_button(self) -> str:
        """
        Generate a push button request sequence for an LCD button.

        This method constructs and returns the string that represents the sequence of key press
        events (key down followed by key up) for the LCD button associated with the `ctrl_name`.
        The request is formatted as a string where each line corresponds to an event.

        :raises ValueError: If `ctrl_name` is not properly set or invalid.
        :return: A string representing the key press sequence for the LCD button.
        """
        return f'{self.ctrl_name} {KEY_DOWN}\n|{self.ctrl_name} {KEY_UP}\n'

    @staticmethod
    def __generate_empty() -> str:
        """
        Generate and return an empty string.

        It does not take any arguments and simply returns an empty string.

        :return: An empty string.
        """
        return ''

    def __generate_cycle_request(self) -> str:
        """
        Generate a cycle request string.

        This method constructs and returns a string representing a button's cycle request.
        It typically combines the control name with the next value intended for the button and appends a newline character at the end.

        :return: A formatted string representing the cycle request, including the control name and the next value for the button.
        """
        return f'{self.ctrl_name} {self._get_next_value_for_button()}\n'

    def __generate_custom_request(self) -> str:
        """
        Generate and formats a custom request string based on the raw request input.

        This method processes the raw request string to extract and properly format its content,
        specifically for custom request types.
        It splits the raw request using the defined delimiter for custom request types and
        re-formats the request content using newline characters.

        :raises AttributeError: If `self.raw_request` is not properly formatted or the expected split pattern is missing.
        :raises IndexError: If the split raw request string does not contain the expected elements after processing.
        :return: A formatted request string with replaced delimiters.
        """
        request = self.raw_request.split(f'{RequestType.CUSTOM.value} ')[1]
        request = request.replace('|', '\n|')
        return request.strip('|')

    def __str__(self) -> str:
        return f'{self.ctrl_name}: {self.raw_request}'


class Color(Enum):
    """A superset of HTML 4.0 color names used in CSS 1."""
    aliceblue = 0xf0f8ff
    antiquewhite = 0xfaebd7
    aqua = 0x00ffff
    aquamarine = 0x7fffd4
    azure = 0xf0ffff
    beige = 0xf5f5dc
    bisque = 0xffe4c4
    black = 0x000000
    blanchedalmond = 0xffebcd
    blue = 0x0000ff
    blueviolet = 0x8a2be2
    brown = 0xa52a2a
    burlywood = 0xdeb887
    cadetblue = 0x5f9ea0
    chartreuse = 0x7fff00
    chocolate = 0xd2691e
    coral = 0xff7f50
    cornflowerblue = 0x6495ed
    cornsilk = 0xfff8dc
    crimson = 0xdc143c
    cyan = 0x00ffff
    darkblue = 0x00008b
    darkcyan = 0x008b8b
    darkgoldenrod = 0xb8860b
    darkgray = 0xa9a9a9
    darkgrey = 0xa9a9a9
    darkgreen = 0x006400
    darkkhaki = 0xbdb76b
    darkmagenta = 0x8b008b
    darkolivegreen = 0x556b2f
    darkorange = 0xff8c00
    darkorchid = 0x9932cc
    darkred = 0x8b0000
    darksalmon = 0xe9967a
    darkseagreen = 0x8fbc8f
    darkslateblue = 0x483d8b
    darkslategray = 0x2f4f4f
    darkslategrey = 0x2f4f4f
    darkturquoise = 0x00ced1
    darkviolet = 0x9400d3
    deeppink = 0xff1493
    deepskyblue = 0x00bfff
    dimgray = 0x696969
    dimgrey = 0x696969
    dodgerblue = 0x1e90ff
    firebrick = 0xb22222
    floralwhite = 0xfffaf0
    forestgreen = 0x228b22
    fuchsia = 0xff00ff
    gainsboro = 0xdcdcdc
    ghostwhite = 0xf8f8ff
    gold = 0xffd700
    goldenrod = 0xdaa520
    gray = 0x808080
    grey = 0x808080
    green = 0x008000
    greenyellow = 0xadff2f
    honeydew = 0xf0fff0
    hotpink = 0xff69b4
    indianred = 0xcd5c5c
    indigo = 0x4b0082
    ivory = 0xfffff0
    khaki = 0xf0e68c
    lavender = 0xe6e6fa
    lavenderblush = 0xfff0f5
    lawngreen = 0x7cfc00
    lemonchiffon = 0xfffacd
    lightblue = 0xadd8e6
    lightcoral = 0xf08080
    lightcyan = 0xe0ffff
    lightgoldenrodyellow = 0xfafad2
    lightgreen = 0x90ee90
    lightgray = 0xd3d3d3
    lightgrey = 0xd3d3d3
    lightpink = 0xffb6c1
    lightsalmon = 0xffa07a
    lightseagreen = 0x20b2aa
    lightskyblue = 0x87cefa
    lightslategray = 0x778899
    lightslategrey = 0x778899
    lightsteelblue = 0xb0c4de
    lightyellow = 0xffffe0
    lime = 0x00ff00
    limegreen = 0x32cd32
    linen = 0xfaf0e6
    magenta = 0xff00ff
    maroon = 0x800000
    mediumaquamarine = 0x66cdaa
    mediumblue = 0x0000cd
    mediumorchid = 0xba55d3
    mediumpurple = 0x9370db
    mediumseagreen = 0x3cb371
    mediumslateblue = 0x7b68ee
    mediumspringgreen = 0x00fa9a
    mediumturquoise = 0x48d1cc
    mediumvioletred = 0xc71585
    midnightblue = 0x191970
    mintcream = 0xf5fffa
    mistyrose = 0xffe4e1
    moccasin = 0xffe4b5
    navajowhite = 0xffdead
    navy = 0x000080
    oldlace = 0xfdf5e6
    olive = 0x808000
    olivedrab = 0x6b8e23
    orange = 0xffa500
    orangered = 0xff4500
    orchid = 0xda70d6
    palegoldenrod = 0xeee8aa
    palegreen = 0x98fb98
    paleturquoise = 0xafeeee
    palevioletred = 0xdb7093
    papayawhip = 0xffefd5
    peachpuff = 0xffdab9
    peru = 0xcd853f
    pink = 0xffc0cb
    plum = 0xdda0dd
    powderblue = 0xb0e0e6
    purple = 0x800080
    rebeccapurple = 0x663399
    red = 0xff0000
    rosybrown = 0xbc8f8f
    royalblue = 0x4169e1
    saddlebrown = 0x8b4513
    salmon = 0xfa8072
    sandybrown = 0xf4a460
    seagreen = 0x2e8b57
    seashell = 0xfff5ee
    sienna = 0xa0522d
    silver = 0xc0c0c0
    skyblue = 0x87ceeb
    slateblue = 0x6a5acd
    slategray = 0x708090
    slategrey = 0x708090
    snow = 0xfffafa
    springgreen = 0x00ff7f
    steelblue = 0x4682b4
    tan = 0xd2b48c
    teal = 0x008080
    thistle = 0xd8bfd8
    tomato = 0xff6347
    turquoise = 0x40e0d0
    violet = 0xee82ee
    wheat = 0xf5deb3
    white = 0xffffff
    whitesmoke = 0xf5f5f5
    yellow = 0xffff00
    yellowgreen = 0x9acd32


class GuiTab(IntEnum):
    """Describe GUI mani window tabs."""
    devices = 0
    settings = 1
    g_keys = 2
    debug = 3


class DllSdk(BaseModel):
    """DLL SDK."""
    name: str
    header_file: str
    directory: str

    @property
    def header(self) -> str:
        """
        Load the header content of the DLL.

        :return: The header content as a string.
        """
        with open(file=Path(__file__) / '..' / 'resources' / f'{self.header_file}') as header_file:
            header = header_file.read()
        return header

    def get_path(self) -> str:
        """
        Return the path of the DLL file based on the provided library type.

        :return: The path of the DLL file as a string.
        """
        arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
        try:
            prog_files = environ['PROGRAMW6432']
        except KeyError:
            prog_files = environ['PROGRAMFILES']
        dll_path = f'{prog_files}\\Logitech Gaming Software\\SDK\\{self.directory}\\{arch}\\Logitech{self.name.capitalize()}.dll'
        return dll_path


LcdDll = DllSdk(name='LCD', directory='LCD', header_file='LogitechLCDLib.h')
LedDll = DllSdk(name='LED', directory='LED', header_file='LogitechLEDLib.h')
KeyDll = DllSdk(name='Gkey', directory='G-key', header_file='LogitechGkeyLib.h')

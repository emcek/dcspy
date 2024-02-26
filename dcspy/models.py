from enum import Enum
from pathlib import Path
from re import search
from tempfile import gettempdir
from typing import Any, Callable, Dict, Final, Iterator, List, Optional, Sequence, Tuple, Union

from packaging import version
from PIL import ImageFont
from pydantic import BaseModel, ConfigDict, RootModel, field_validator

# Network
SEND_ADDR: Final = ('127.0.0.1', 7778)
RECV_ADDR: Final = ('', 5010)
MULTICAST_IP: Final = '239.255.50.10'

# LCD types
TYPE_MONO: Final = 1
TYPE_COLOR: Final = 2

# LCD Monochrome size
MONO_WIDTH: Final = 160
MONO_HEIGHT: Final = 43

# LCD Color size
COLOR_WIDTH: Final = 320
COLOR_HEIGHT: Final = 240

# LED constants
LOGI_LED_DURATION_INFINITE: Final = 0
LOGI_DEVICETYPE_MONOCHROME: Final = 1
LOGI_DEVICETYPE_RGB: Final = 2
LOGI_DEVICETYPE_ALL: Final = LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB

# G Key
LOGITECH_MAX_GKEYS: Final = 30
LOGITECH_MAX_M_STATES: Final = 4

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
}


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
    """FixedStep input interface of inputs section of Control."""
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
    """VariableStep input interface of inputs section of Control."""
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
    """SetState input interface of inputs section of Control."""
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
    """Action input interface of inputs section of Control."""
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


class SetString(Input):
    """SetString input interface of inputs section of Control."""
    interface: str = 'set_string'

    @field_validator('interface')
    def validate_interface(cls, value):
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
    """String output interface of outputs section of Control."""
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
    """Integer output interface of outputs section of Control."""
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


class PhysicalVariant(Enum):
    """Physical variants of BIOS selectors."""

    PUSH_BUTTON = 'push_button'
    TOGGLE_SWITCH = 'toggle_switch'
    THREE_POSITION_SWITCH = '3_position_switch'
    INFINITE_ROTARY = 'infinite_rotary'
    LIMITED_ROTARY = 'limited_rotary'
    ROCKER_SWITCH = 'rocker_switch'
    BUTTON_LIGHT = 'button_light'
    EMPTY = None


class ControlKeyData:
    """Describes input data for cockpit controller."""

    def __init__(self, name: str, description: str, max_value: int, suggested_step: int = 1, physical_variant: PhysicalVariant = PhysicalVariant.EMPTY) -> None:
        """
        Define type of input for cockpit controller.

        :param name: name of the input
        :param description: short description
        :param max_value: max value (zero based)
        :param suggested_step: 1 by default
        :param physical_variant: physical variant of cockpit controller, EMPTY by default
        """
        self.name = name
        self.description = description
        self.max_value = max_value
        self.suggested_step = suggested_step
        self.list_dict: List[Union[FixedStep, VariableStep, SetState, Action, SetString]] = []
        self.physical_variant = physical_variant

    def __repr__(self) -> str:
        return f'KeyControl({self.name}: {self.description} - max_value={self.max_value}, suggested_step={self.suggested_step}, {self.physical_variant})'

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
        instance = cls(name=ctrl.identifier, description=ctrl.description, max_value=max_value, suggested_step=suggested_step,
                       physical_variant=ctrl.physical_variant)
        instance.list_dict = ctrl.inputs
        return instance

    @staticmethod
    def _get_max_value(list_of_dicts: List[Union[FixedStep, VariableStep, SetState, Action, SetString]]) -> int:
        """
        Get max value from list of dictionaries.

        :param list_of_dicts:
        :return: max value
        """
        _real_zero = False
        _max_values = []
        for d in list_of_dicts:
            try:
                _max_values.append(d.max_value)  # type: ignore
                if d.max_value == 0:             # type: ignore
                    _real_zero = True
                    break
            except AttributeError:
                _max_values.append(0)
        max_value = max(_max_values)
        if all([not _real_zero, not max_value]):
            max_value = 1
        return max_value

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
        return any(isinstance(d, FixedStep) for d in self.list_dict)

    @property
    def has_variable_step(self) -> bool:
        """
        Check if input has variable step input.

        :return: bool
        """
        return any(isinstance(d, VariableStep) for d in self.list_dict)

    @property
    def has_set_state(self) -> bool:
        """
        Check if input has set state input.

        :return: bool
        """
        return any(isinstance(d, SetState) for d in self.list_dict)

    @property
    def has_action(self) -> bool:
        """
        Check if input has action input.

        :return: bool
        """
        return any(isinstance(d, Action) for d in self.list_dict)

    @property
    def has_set_string(self) -> bool:
        """
        Check if input has set string input.

        :return: bool
        """
        return any(isinstance(d, SetString) for d in self.list_dict)

    @property
    def is_push_button(self) -> bool:
        """
        Check if the controller is a push button type.

        :return: bool
        """
        push_btn = self.physical_variant is PhysicalVariant.PUSH_BUTTON
        two_states = self.has_fixed_step and self.has_set_state and self.max_value == 1
        return push_btn or two_states


class Control(BaseModel):
    """Control section of BIOS model."""
    api_variant: Optional[str] = None
    category: str
    control_type: str
    description: str
    identifier: str
    inputs: List[Union[FixedStep, VariableStep, SetState, Action, SetString]]
    momentary_positions: Optional[str] = None
    outputs: List[Union[OutputStr, OutputInt]]
    physical_variant: PhysicalVariant = PhysicalVariant.EMPTY

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
    root: Dict[str, Dict[str, Control]]

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

    def get_inputs(self) -> Dict[str, Dict[str, ControlKeyData]]:
        """
        Get dict with all not empty inputs for plane.

        Inputs are grouped in original sections.

        :return: Dict with sections and ControlKeyData models.
        """
        ctrl_key: Dict[str, Dict[str, ControlKeyData]] = {}

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
            'rb_set_state': f'{ctrl_key.name} CYCLE {ctrl_key.suggested_step} {ctrl_key.max_value}',
            'rb_custom': f'{ctrl_key.name} CUSTOM {custom_value}',
            'rb_button': f'{ctrl_key.name} PUSH_BUTTON',
            'rb_variable_step_plus': f'{ctrl_key.name} +{ctrl_key.suggested_step}',
            'rb_variable_step_minus': f'{ctrl_key.name} -{ctrl_key.suggested_step}'
        }
        return cls(identifier=ctrl_key.name, request=rb_iface_request[rb_iface], widget_iface=rb_iface)

    @classmethod
    def from_plane_gkeys(cls, /, plane_gkeys: Dict[str, str]) -> Dict[str, 'GuiPlaneInputRequest']:
        """
        Generate GuiPlaneInputRequest from plane_gkeys yaml.

        :param plane_gkeys:
        :return:
        """
        input_reqs = {}
        req_keyword_rb_iface = {
            'CUSTOM': 'rb_custom',
            'PUSH_BUTTON': 'rb_button',
            'TOGGLE': 'rb_action',
            'INC': 'rb_fixed_step_inc',
            'DEC': 'rb_fixed_step_dec',
            'CYCLE': 'rb_set_state',
            '+': 'rb_variable_step_plus',
            '-': 'rb_variable_step_minus',
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


class FontsConfig(BaseModel):
    """Fonts configuration for LcdInfo."""
    name: str
    small: int
    medium: int
    large: int


class LcdInfo(BaseModel):
    """LCD info."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    width: int
    height: int
    type: LcdType
    foreground: Union[int, Tuple[int, int, int, int]]
    background: Union[int, Tuple[int, int, int, int]]
    mode: LcdMode
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


LcdMono = LcdInfo(width=MONO_WIDTH, height=MONO_HEIGHT, type=LcdType.MONO, foreground=255,
                  background=0, mode=LcdMode.BLACK_WHITE)
LcdColor = LcdInfo(width=COLOR_WIDTH, height=COLOR_HEIGHT, type=LcdType.COLOR, foreground=(0, 255, 0, 255),
                   background=(0, 0, 0, 0), mode=LcdMode.TRUE_COLOR)


class KeyboardModel(BaseModel):
    """Light LCD keyboard model."""
    name: str
    klass: str
    modes: int
    gkeys: int
    lcdkeys: Sequence[LcdButton]
    lcd: str


ModelG19 = KeyboardModel(name='G19', klass='G19', modes=3, gkeys=12, lcd='color',
                         lcdkeys=(LcdButton.LEFT, LcdButton.RIGHT, LcdButton.OK, LcdButton.CANCEL, LcdButton.UP, LcdButton.DOWN, LcdButton.MENU))
ModelG13 = KeyboardModel(name='G13', klass='G13', modes=3, gkeys=29, lcd='mono',
                         lcdkeys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))
ModelG15v1 = KeyboardModel(name='G15 v1', klass='G15v1', modes=3, gkeys=18, lcd='mono',
                           lcdkeys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))
ModelG15v2 = KeyboardModel(name='G15 v2', klass='G15v2', modes=3, gkeys=6, lcd='mono',
                           lcdkeys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))
ModelG510 = KeyboardModel(name='G510', klass='G510', modes=3, gkeys=18, lcd='mono',
                          lcdkeys=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR))

KEYBOARD_TYPES = [ModelG19.klass, ModelG510.klass, ModelG15v1.klass, ModelG15v2.klass, ModelG13.klass]


class Gkey(BaseModel):
    """Logitech G-Key."""
    key: int
    mode: int

    def __str__(self):
        """Return with format G<i>/M<j>."""
        return f'G{self.key}_M{self.mode}'

    def __bool__(self):
        """Return False when any of value is zero."""
        return all([self.key, self.mode])

    def __hash__(self):
        """Hash will be the same for any two Gkey instances with the same key and mode values."""
        return hash((self.key, self.mode))

    @classmethod
    def from_yaml(cls, /, yaml_str: str) -> 'Gkey':
        """
        Construct Gkey from YAML string.

        :param yaml_str: ex. G2_M1
        :return: Gkey instance
        """
        match = search(r'G(\d+)_M(\d+)', yaml_str)
        if match:
            return cls(**{k: int(i) for k, i in zip(('key', 'mode'), match.groups())})
        raise ValueError(f'Invalid Gkey format: {yaml_str}. Expected: G<i>_M<j>')

    @staticmethod
    def generate(key: int, mode: int) -> Sequence['Gkey']:
        """
        Generate sequence of G-Keys.

        :param key: number of keys
        :param mode: number of modes
        :return:
        """
        return tuple([Gkey(key=k, mode=m) for k in range(1, key + 1) for m in range(1, mode + 1)])

    @staticmethod
    def name(row: int, col: int) -> str:
        """
        Return Gkey as string for row and col.

        :param row: row number, zero based
        :param col: column number, zero based
        """
        return str(Gkey(key=row + 1, mode=col + 1))


def get_key_instance(key_str: str) -> Union[Gkey, LcdButton]:
    """
    Get key instance from string.

    :param key_str: key name from yaml configuration
    :return: Gkey or LcdButton instance
    """
    try:
        key = Gkey.from_yaml(key_str)
    except ValueError:
        key = getattr(LcdButton, key_str)
    return key


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


DcspyConfigYaml = Dict[str, Union[str, int, bool]]


class Direction(Enum):
    """Direction of iteration."""
    FORWARD = 1
    BACKWARD = -1


class ZigZagIterator:
    """Iterate with values from 0 to max_val and back."""
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

    def __iter__(self):
        return self

    def __str__(self):
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

        :param value: Direction.FORWARD or Direction.BACKWARD
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
    key: Union[LcdButton, Gkey]

    @field_validator('ctrl_name')
    def validate_interface(cls, value):
        """
        Validate.

        :param value:
        :return:
        """
        if not value or not all(ch.isupper() or ch == '_' or ch.isdigit() for ch in value):
            raise ValueError("Invalid value for 'ctrl_name'. Only A-Z, 0-9 and _ are allowed.")
        return value

    @classmethod
    def from_request(cls, key: Union[LcdButton, Gkey], request: str, get_bios_fn: Callable[[str], Union[str, int, float]]) -> 'RequestModel':
        """
        Build object based on string request.

        For cycle request `get_bios_fn` is used to update current value of BIOS selector.

        :param key: LcdButton or Gkey
        :param request: The raw request string.
        :param get_bios_fn: A callable function that return current value for BIOS selector.
        :return: An instance of the RequestModel class.
        """
        cycle_button = CycleButton(ctrl_name='', step=0, max_value=0)
        if RequestType.CYCLE.value in request:
            cycle_button = CycleButton.from_request(request)
        ctrl_name = request.split(' ')[0]
        return RequestModel(ctrl_name=ctrl_name, raw_request=request, get_bios_fn=get_bios_fn, cycle=cycle_button, key=key)

    @classmethod
    def empty(cls, key: Union[LcdButton, Gkey]) -> 'RequestModel':
        """
        Create an empty request model, for key which isn't assign.

        :param key: LcdButton or Gkey
        :return: The created request model.
        """
        return RequestModel(ctrl_name='EMPTY', raw_request='', get_bios_fn=int, cycle=CycleButton(ctrl_name='', step=0, max_value=0), key=key)

    def _get_next_value_for_button(self) -> int:
        """Get next int value (cycle fore and back) for ctrl_name BIOS selector."""
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

    def bytes_requests(self, key_down: Optional[int] = None) -> List[bytes]:
        """
        Generate list of bytes that represent the individual requests based on the current state of the model.

        :param key_down: 1 indicate when G-Key was push down, 0 when G-Key is up
        :return: a list of bytes representing the individual requests
        """
        if self.is_cycle:
            request = f'{self.ctrl_name} {self._get_next_value_for_button()}\n'
        elif self.is_custom:
            request = self.raw_request.split(f'{RequestType.CUSTOM.value} ')[1]
            request = request.replace('|', '\n|')
            request = request.strip('|')
        elif self.is_push_button and isinstance(self.key, LcdButton):
            request = f'{self.ctrl_name} 1\n|{self.ctrl_name} 0\n'
        elif self.is_push_button and isinstance(self.key, Gkey) and key_down:
            request = f'{self.ctrl_name} 1\n'
        elif self.is_push_button and isinstance(self.key, Gkey) and not key_down:
            request = f'{self.ctrl_name} 0\n'
        else:
            request = f'{self.raw_request}\n'
        return [bytes(req, 'utf-8') for req in request.split('|')]

    def __str__(self) -> str:
        return f'{self.ctrl_name}: {self.raw_request}'

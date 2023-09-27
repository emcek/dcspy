from typing import Dict, List, Optional, Union

from pydantic import BaseModel, RootModel, field_validator

CTRL_LIST_SEPARATOR = '--'


class Input(BaseModel):
    description: str

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item, default=None):
        """
        Access item and get default when is not available.

        :param item:
        :param default:
        :return:
        """
        return getattr(self, item, default)


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
        :param description: Description
        :param max_value: max value
        :param suggested_step: 1 by default
        """
        self.name = name
        self.description = description
        self.max_value = max_value
        self.suggested_step = suggested_step
        self.list_dict: List[Union[FixedStep, VariableStep, SetState, Action]] = []

    def __repr__(self) -> str:
        return f'KeyControl({self.description}: {self.name}, max_value={self.max_value}, suggested_step={self.suggested_step})'

    def __bool__(self) -> bool:
        if not all([self.max_value, self.suggested_step]):
            return False
        return True

    @classmethod
    def from_dicts(cls, /, name, description, list_of_dicts: List[Union[FixedStep, VariableStep, SetState, Action]]) -> 'ControlKeyData':
        """
        Construct object from list of dictionaries.

        :param name: name of the input
        :param description:
        :param list_of_dicts:
        :return: ControlKeyData instance
        """
        max_value = max(d.get('max_value', 1) for d in list_of_dicts)
        suggested_step = max([d.get('suggested_step', 1) for d in list_of_dicts])
        instance = cls(name=name, description=description, max_value=max_value, suggested_step=suggested_step)
        instance.list_dict = list_of_dicts
        return instance

    @property
    def input_len(self) -> int:
        return len(self.list_dict)

    @property
    def one_input(self) -> bool:
        return bool(len(self.list_dict) == 1)

    @property
    def has_fixed_step(self) -> bool:
        return any([isinstance(d, FixedStep) for d in self.list_dict])

    @property
    def has_variable_step(self) -> bool:
        return any([isinstance(d, VariableStep) for d in self.list_dict])

    @property
    def has_set_state(self) -> bool:
        return any([isinstance(d, SetState) for d in self.list_dict])

    @property
    def has_action(self) -> bool:
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

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, RootModel, field_validator


class Input(BaseModel):
    description: str

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item, default=None):
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


class Control(BaseModel):
    category: str
    control_type: str
    description: str
    identifier: str
    inputs: List[Union[FixedStep, VariableStep, SetState, Action]]
    momentary_positions: Optional[str] = None
    outputs: List[Union[OutputStr, OutputInt]]
    physical_variant: Optional[str] = None

    @property
    def input(self):
        max_value = max(d.get('max_value', 1) for d in self.inputs)
        suggested_step = max([d.get('suggested_step', 1) for d in self.inputs])
        return {'description': self.description, 'max_value': max_value, 'suggested_step': suggested_step}

    @property
    def output(self):
        if isinstance(self.outputs[0], OutputInt):
            return {'klass': 'IntegerBuffer', 'args': {'address': self.outputs[0].address, 'mask': self.outputs[0].mask, 'shift_by': self.outputs[0].shift_by}, 'value': int(), 'max_value': self.outputs[0].max_value}
        else:
            return {'klass': 'StringBuffer', 'args': {'address': self.outputs[0].address, 'max_length': self.outputs[0].max_length}, 'value': ''}


# DcsBios = RootModel(Dict[str, Dict[str, Control]])

class DcsBios(RootModel):
    root: Dict[str, Dict[str, Control]]

    def __str__(self):
        """
        Show details of DcsBios.

        :return: string
        """
        return str(self.root)

    def __getitem__(self, item):
        # https://github.com/pydantic/pydantic/issues/1802
        return self.__root__[item]

    def get(self, item, default=None):
        return getattr(self.__root__, item, default)


class ControlKeyData:
    def __init__(self, description: str, max_value: int, suggested_step: int = 1) -> None:
        """
        Define type of input for cockpit controller.

        :param description: Description
        :param max_value: max value
        :param suggested_step: 1 by default
        """
        self.max_value = max_value
        self.suggested_step = suggested_step
        self.description = description

    @classmethod
    def from_dicts(cls, /, description, list_of_dicts: List[Dict[str, int]]) -> 'ControlKeyData':
        """
        Construct object form list of dictionaries.

        :param description:
        :param list_of_dicts:
        :return: ControlKeyData instance
        """
        max_value = max(dictionary.get('max_value', 1) for dictionary in list_of_dicts)
        suggested_step = max([dictionary.get('suggested_step', 1) for dictionary in list_of_dicts])
        return cls(description=description, max_value=max_value, suggested_step=suggested_step)

    def __repr__(self) -> str:
        """
        Show details of ControlKeyData.

        :return: string
        """
        return f'KeyControl({self.description}: max_value={self.max_value}, suggested_step={self.suggested_step})'
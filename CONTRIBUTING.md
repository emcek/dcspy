## Development
DCSpy use multicast UDP to receive/send data from/to DCS-BIOS as describe [here](https://github.com/DCSFlightpanels/dcs-bios/blob/master/Scripts/DCS-BIOS/doc/developerguide.adoc).
Main modules of DCSpy:
* `run.py` main script - it starts GUI in tkinter
* `starter.py` responsible for initialise DCS-BIOS parser, Logitech G13/G15/G510 Mono handler and G19 Color handler, as well as running connection to DCS.
* `log.py` dumb simple logger configuration
* `logitech.py` handling Logitech keyboards with LCD and buttons, loading dynamically current aircraft
* `aircraft.py` are define all supported aircraft with details how and what and display from DCS, draws bitmap that will be passed to LCD keyboard handler and returns input data for buttons under LCD
* `dcsbios.py` BIOS protocol parser and two buffers to fetching integer and string values `IntegerBuffer` and `StringBuffer` respectively.
* `tk_gui.py` simple GUI with widgets, layouts and events. It allows configuring DCSpy as well.
* `utils.py` various useful tools - load and save config, check online version or download file

If you want to modify or write something by yourself, here's a quick walk-through:
* Each plane has special dict:
```python
class IntBuffArgs(TypedDict):
    address: int
    mask: int
    shift_by: int

class StrBuffArgs(TypedDict):
    address: int
    max_length: int

class BiosValue(TypedDict):
    klass: str
    args: Union[StrBuffArgs, IntBuffArgs]
    value: Union[int, str]
    max_value: NotRequired[int]

class Ka50(Aircraft):
    def __init__(self, lcd_type: LcdInfo) -> None:
        super().__init__(lcd_type)
        self.bios_data: Dict[str, BiosValue] = {
            'PVI_LINE2_TEXT': {'klass': 'StringBuffer',
                               'args': {'address': 0x192a, 'max_length': 6},
                               'value': str()},
            'AP_ALT_HOLD_LED': {'klass': 'IntegerBuffer',
                                'args': {'address': 0x1936, 'mask': 0x8000, 'shift_by': 0xf},
                                'value': int()},
            'IFF_MASTER_KNB': {'klass': 'IntegerBuffer',
                               'args': {'address': 0x4450, 'mask': 0xe, 'shift_by': 0x1},
                               'value': int(),
                               'max_value': 4}}
```
which describe data to be fetched from DCS-BIOS with buffer class and its parameters. For required address and data max_length, look up in `C:\Users\xxx\Saved Games\DCS.openbeta\Scripts\DCS-BIOS\doc\control-reference.html`
* Then after detecting current plane in DCS, `KeyboardMono` or `KeyboardColor` will load instance of aircraft as `plane`
```python
self.plane: Aircraft = getattr(import_module('dcspy.aircraft'), self.plane_name)(self.lcd)
```
* and "subscribe" for changes with callback for all fields defined in `plane` instance.  
  First line in for loop load `StringBuffer` or `IntegerBuffer` object for given `field_name` from plane's `bios_data` i.e `PVI_LINE2_TEXT`.  
  Second, create instance of buffer and pass `parser`, callback function )by default `set_bios` and rest of DCS-BIOS protocol arguments: `address` and `max_length` or `address`, `mask` and `shift_by`.
```python
for field_name, proto_data in self.plane.bios_data.items():
    buffer = getattr(import_module('dcspy.dcsbios'), proto_data['klass'])
    buffer(parser=self.parser, callback=partial(self.plane.set_bios, field_name), **proto_data['args'])
```
* when, receive bytes, parser will process data:
```python
dcs_bios_resp = sock.recv(2048)
for int_byte in dcs_bios_resp:
    parser.process_byte(int_byte)
```
and calls callback function `set_bios()` of current `plane` with received value and update display content, by creating bitmap and passing it through Logitech LCD SDK to device display.

* You can also use 4 buttons for (G13/G15/G510) and 7 buttons (G19), just check their state with `check_buttons()`, which one is pressed and send request do DCS-BIOS.
```python
sock.sendto(bytes(self.plane.button_request(button), 'utf-8'), ('127.0.0.1', 7778))
```
* Correct action is define in aircraft instance `button_request()` method:
```python
class LcdButton(Enum):
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

def button_request(self, button: LcdButton, request: str = '\n') -> str:
    action = {LcdButton.ONE: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
              LcdButton.TWO: 'UFC_COMM1_CHANNEL_SELECT INC\n',
              LcdButton.THREE: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
              LcdButton.FOUR: 'UFC_COMM2_CHANNEL_SELECT INC\n',
              LcdButton.LEFT: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
              LcdButton.RIGHT: 'UFC_COMM1_CHANNEL_SELECT INC\n',
              LcdButton.DOWN: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
              LcdButton.UP: 'UFC_COMM2_CHANNEL_SELECT INC\n'}
    return super().button_request(button, action.get(button, '\n'))
```
Again, look it up in `control-reference.html`, in example above, COMM1 and COMM2 knobs of F/A-18C will rotate left and right.

* If there is button/switch, with more then two state, you can cycle thru fore and back, by using `get_next_value_for_button()` in `button_request()`

```python
def button_request(self, button: LcdButton, request: str = '\n') -> str:
    button_map = {LcdButton.OK: 'HUD_ATT_SW', 
                  LcdButton.CANCEL: 'IFEI_UP_BTN', 
                  LcdButton.MENU: 'IFEI_DWN_BTN'}
    settings = 0
    button_bios_name = ''
    if button in button_map:
        button_bios_name = button_map[button]
        settings = self.get_next_value_for_button(button_bios_name)
    action = {LcdButton.ONE: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
              ...
              LcdButton.UP: 'UFC_COMM2_CHANNEL_SELECT INC\n',
              LcdButton.MENU: f'{button_bios_name} {settings}\n',
              LcdButton.CANCEL: f'{button_bios_name} {settings}\n',
              LcdButton.OK: f'{button_bios_name} {settings}\n'}
    return super().button_request(button, action.get(button, '\n'))
```
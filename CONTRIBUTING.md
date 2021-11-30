## Development
DCSpy use multicast UDP to receive/send data from/to DCS-BIOS as describe [here](https://github.com/DCSFlightpanels/dcs-bios/blob/master/Scripts/DCS-BIOS/doc/developerguide.adoc).  
Main modules of DCSpy:
* `dcspy.py` main script - it starts GUI in tkinter
* `starter.py` responsible for initialise DCS-BIOS parser, Logitech G13/G15/G510 Mono handler and G19 Color handler, as well as running connection to DCS.
* `log.py` dumb simple logger configuration
* `logitech.py` handling Logitech keyboards with LCD and buttons, loading dynamically current aircraft
* `aircrafts.py` are define all supported aircraft with details how and what and display from DCS, draws bitmap that will be passed to LCD keyboard handler and returns input data for buttons under LCD
* `dcsbios.py` BIOS protocol parser and two buffers to fetching integer and string values `IntegerBuffer` and `StringBuffer` respectively.
* `tk_gui.py` simple GUI with widgets, layouts and events. It allows configuring DCSpy as well.
* `utils.py` various useful tools - load and save config, check online version or download file

If you want to modify or write something by yourself, here's a quick walk-through:
* Each plane has special dict:
```python
BIOS_VALUE = TypedDict('BIOS_VALUE', {'class': str, 'args': Dict[str, int], 'value': Union[int, str], 'max_value': int}, total=False)

self.bios_data: Dict[str, BIOS_VALUE] = {
    'PVI_LINE2_TEXT': {'class': 'StringBuffer',
                       'args': {'address': 0x192a, 'max_length': 6},
                       'value': str()},
    'AP_ALT_HOLD_LED': {'class': 'IntegerBuffer', 
                        'args': {'address': 0x1936, 'mask': 0x8000, 'shift_by': 0xf}, 
                        'value': int()}}
```
which describe data to be fetched from DCS-BIOS with buffer class and its parameters. For required address and data max_length, look up in `C:\Users\xxx\Saved Games\DCS.openbeta\Scripts\DCS-BIOS\doc\control-reference.html`
* Then after detecting current plane in DCS, `KeyboardMono` or `KeyboardColor` will load instance of aircraft as `plane`
```python
self.plane: Aircraft = getattr(import_module('dcspy.aircrafts'), self.plane_name)(self.lcd)
```
* and "subscribe" for changes with callback for all fields defined in `plane` instance
```python
for field_name, proto_data in self.plane.bios_data.items():
    buffer = getattr(import_module('dcspy.dcsbios'), proto_data['class'])
    buffer(parser=self.parser, callback=partial(self.plane.set_bios, field_name), **proto_data['args'])
```
* when, receive bytes, parser will process data:
```python
dcs_bios_resp = sock.recv(2048)
for int_byte in dcs_bios_resp:
    parser.process_byte(int_byte)
```
and calls callback function `set_bios()` of current `plane` with received value and update display content, by creating bitmap and passing it through LCD SDK to device display.

* You can also use 4 buttons below LCD (G13) and left, right, up and down buttons (G19), just check their state with `check_buttons()` of `KeyboardMono` which one is pressed and send request do DCS-BIOS.
```python
sock.sendto(bytes(self.plane.button_request(button), 'utf-8'), ('127.0.0.1', 7778))
```
* Correct action is define in aircraft instance `button_request()` method:
```python
action = {1: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
          2: 'UFC_COMM1_CHANNEL_SELECT INC\n',
          3: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
          4: 'UFC_COMM2_CHANNEL_SELECT INC\n',
          9: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
          10: 'UFC_COMM1_CHANNEL_SELECT INC\n',
          14: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
          13: 'UFC_COMM2_CHANNEL_SELECT INC\n'}
return super().button_request(button, action.get(button, '\n'))
```
Again, look it up in `control-reference.html`, in example above, COMM1 and COMM2 knobs of F/A-18C will rotate left and right.

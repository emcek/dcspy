## Development
* `dcspy.py` is responsible for initialise parser, G13 handler, as well as running connection with DCS.
* `logitech.py` is responsible for initialise aircraft specific file and handling G13 display and buttons
* `aircrafts.py` are define all supported aircrafts with details how to handle and display data from DCS, draws bitmap that will be passed to G13 handler and returns input data for buttons under G13 display

If you want to modify or write something by yourself, here's a quick walkthrough:
* Each plan has special dict:
```python
BIOS_VALUE = TypedDict('BIOS_VALUE', {'addr': int, 'len': int, 'val': str})
self.bios_data: Dict[str, BIOS_VALUE] = {
    'ScratchpadStr1': {'addr': 0x744e, 'len': 2, 'val': ''},
    'FuelTotal': {'addr': 0x748a, 'len': 6, 'val': ''}}
```
which describe data to be fetch from DCS-BIOS. For required address and data length, look up in `C:\Users\xxx\Saved Games\DCS.openbeta\Scripts\DCS-BIOS\doc\control-reference.html`
* Then after detecting current plane in DCS, G13 will load instance of aircraft as `plane`
```python
self.plane: Aircraft = getattr(import_module('dcspy.aircrafts'), self.plane_name)(self.g13_lcd.width, self.g13_lcd.height)
```
* and "subscribe" for changes with callback for all fields defined in `plane` instance
```python
for field_name, proto_data in self.plane.bios_data.items():
    StringBuffer(self.parser, proto_data['addr'], proto_data['len'], partial(self.plane.set_bios, field_name))
```
* when, receive byte, parser will process data:
```python
dcs_bios_resp = sock.recv(1)
parser.process_byte(dcs_bios_resp)
```
and calls callback function `set_bios()` of current `plane` with received value and update display content, by creating bitmap and passing it through LCD SDK to device display.

* You can also use 4 button below LCD display, just check their state with `g13.check_buttons()` which one is pressed and send request do DCS-BIOS.
```python
sock.send(bytes(self.plane.button_request(button), 'utf-8'))
```
* Correct action is define in aircraft instance `button_request()` method:
```python
action = {1: 'UFC_COMM1_CHANNEL_SELECT DEC',
          2: 'UFC_COMM1_CHANNEL_SELECT INC',
          3: 'UFC_COMM2_CHANNEL_SELECT DEC',
          4: 'UFC_COMM2_CHANNEL_SELECT INC'}
return f'{action[button]}\n'
```
Again, look it up in `control-reference.html`, in example above, COMM1 and COMM2 knobs of F/A-18C will rotate left and right.

from PiicoDev_RGB import PiicoDev_RGB
import json

JSON_PATH = '/home/controller/display.json'

# LED RBG colours.
RED     = [255, 0, 0]
GREEN   = [0, 255, 0]
BLUE    = [0, 0, 255]
YELLOW  = [255, 255, 0]
CYAN    = [0, 255, 255]
MAGENTA = [255, 0, 255]
WHITE   = [255, 255, 255]
CLEAR   = [0, 0, 0]

LED_INDEX = {
    'r': 0, #LED0: Read
    'w': 1, #LED1: Write
    's': 2  #LED2: Server
}

class Display():
    def __init__(self, mode):
        self._mode = LED_INDEX[mode]
        self._light_output = PiicoDev_RGB()
        self._state = self._read_state()
        self._set_display()

    def __enter__(self):
        self._set_light(self._mode, colour=GREEN)

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is not None:
            self._set_light(self._mode, colour=RED)
        else:
            self._set_light(self._mode, colour=CLEAR)

    # Sets all LEDs to the saved values.
    def _set_display(self):
        for key_led_index, value_colour in self._state.items():
            self._set_light(key_led_index, value_colour)

    # Set read/write/server LED to given colour.
    def _set_light(self, led_index, colour):
        try:
            self._light_output.setPixel(led_index, colour)
            self._light_output.show()
            self._state[self._mode] = colour
            self._write_state()
        except:
            pass

    # Read saved display state from JSON file.
    def _read_state(self):
        state = {}
        try:
            with open(JSON_PATH, 'r') as file:
                raw_state = json.load(file)
                for key, values in raw_state.items():
                    state[int(key)] = [int(value) for value in values]
        except:
            state = {
                LED_INDEX['r']: CLEAR,
                LED_INDEX['w']: CLEAR,
                LED_INDEX['s']: CLEAR
            }
        finally:
            return state

    # Write display state to JSON file.
    def _write_state(self):
        with open(JSON_PATH, 'w') as file:
            json.dump(self._state, file)
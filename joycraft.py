#!/usr/bin/env python3

import logging
import evdev
from evdev import InputDevice, list_devices, categorize, ecodes
import select
import time
from daemon import DaemonContext

# List of known base names or keywords
KNOWN_DEVICES = [
     "Wireless Controller",
     "Stadia"]

EXCLUDED_DEVICES = [
     "Wireless Controller Touchpad",
     "Wireless Controller Motion Sensors"
]

def is_supported_gamepad(device_name):
    if any(pattern in device_name for pattern in EXCLUDED_DEVICES):
        return False

    return any(pattern in device_name for pattern in KNOWN_DEVICES)

def get_gamepads():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    logging.debug('Found device: %s', [dev.name for dev in devices])
    gamepads = [dev for dev in devices if is_supported_gamepad(dev.name)]
    logging.debug('Gamepads: %s', gamepads)
    return gamepads

def handle_events(device):
	"""
	Handle input events from a gamepad device.
	"""
	for event in device.read_loop():
		if event.type == evdev.ecodes.EV_KEY:
			key_event = categorize(event)
			if key_event.keystate == key_event.key_down:
				print(f"{device.path} - {key_event.keycode} pressed")
			else:
				print(f"{device.path} - {key_event.keycode} released")
		elif event.type == evdev.ecodes.EV_ABS:
			if event.code in (evdev.ecodes.ABS_X, evdev.ecodes.ABS_Y, evdev.ecodes.ABS_RX, evdev.ecodes.ABS_RY, evdev.ecodes.ABS_Z, evdev.ecodes.ABS_RZ):
				print(f"{device.path} - {event.code} moved to {event.value}")
			elif event.code == evdev.ecodes.ABS_HAT0X:
				direction = "Right" if event.value == 1 else ("Left" if event.value == -1 else "Center")
				print(f"{device.path} - D-pad X moved to {direction}")
			elif event.code == evdev.ecodes.ABS_HAT0Y:
				direction = "Down" if event.value == 1 else ("Up" if event.value == -1 else "Center")
				print(f"{device.path} - D-pad Y moved to {direction}")


def main():
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
    devices = get_gamepads()

    if not devices:
        logging.info("No gamepads found. Waiting for gamepads to be connected...")

    while True:
        if not devices:
            time.sleep(5)  # wait for 5 seconds before checking for gamepads again
            devices = get_gamepads()
            continue

        logging.info('Waiting for events from devices: %s', devices)
        try:
            r, w, x = select.select(devices, [], [])
            for dev in r:
                handle_events(dev)
        except OSError:
            # Handles cases where a device gets disconnected and throws an OSError.
            devices.remove(dev)

if __name__ == "__main__":
    main()


from enum import IntEnum
from math import log

import obsws_python as obs

LEVELTYPE = IntEnum(
    "LEVELTYPE",
    "VU POSTFADER PREFADER",
    start=0,
)


def on_input_mute_state_changed(data):
    """An input's mute state has changed."""
    if data.input_name == DEVICE:
        print(f"{DEVICE} mute toggled")


def on_input_volume_meters(data):
    """volume level update every 50 milliseconds"""

    def fget(x):
        return round(20 * log(x, 10), 1) if x > 0 else -200.0

    for device in data.inputs:
        name = device["inputName"]
        if name == DEVICE and device["inputLevelsMul"]:
            left, right = device["inputLevelsMul"]
            print(
                f"{name} [L: {fget(left[LEVELTYPE.POSTFADER])}, R: {fget(right[LEVELTYPE.POSTFADER])}]",
            )


def main():
    client = obs.EventClient(subs=(obs.Subs.LOW_VOLUME | obs.Subs.INPUTVOLUMEMETERS))
    client.callback.register([on_input_volume_meters, on_input_mute_state_changed])

    while cmd := input("<Enter> to exit>\n"):
        if not cmd:
            break


if __name__ == "__main__":
    DEVICE = "Desktop Audio"

    main()

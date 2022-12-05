from enum import IntFlag


class Subs(IntFlag):
    GENERAL = 1 << 0
    CONFIG = 1 << 1
    SCENES = 1 << 2
    INPUTS = 1 << 3
    TRANSITIONS = 1 << 4
    FILTERS = 1 << 5
    OUTPUTS = 1 << 6
    SCENEITEMS = 1 << 7
    MEDIAINPUTS = 1 << 8
    VENDORS = 1 << 9
    UI = 1 << 10

    LOW_VOLUME = (
        GENERAL
        | CONFIG
        | SCENES
        | INPUTS
        | TRANSITIONS
        | FILTERS
        | OUTPUTS
        | SCENEITEMS
        | MEDIAINPUTS
        | VENDORS
        | UI
    )

    INPUTVOLUMEMETERS = 1 << 16
    INPUTACTIVESTATECHANGED = 1 << 17
    INPUTSHOWSTATECHANGED = 1 << 18
    SCENEITEMTRANSFORMCHANGED = 1 << 19

    HIGH_VOLUME = (
        INPUTVOLUMEMETERS
        | INPUTACTIVESTATECHANGED
        | INPUTSHOWSTATECHANGED
        | SCENEITEMTRANSFORMCHANGED
    )

    ALL = LOW_VOLUME | HIGH_VOLUME

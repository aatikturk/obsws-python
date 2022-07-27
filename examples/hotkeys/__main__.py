import inspect

import keyboard
import obsstudio_sdk as obs


class Observer:
    def __init__(self, cl):
        self._cl = cl
        self._cl.callback.register(self.on_current_program_scene_changed)
        print(f"Registered events: {self._cl.callback.get()}")

    @property
    def event_identifier(self):
        return inspect.stack()[1].function

    def on_current_program_scene_changed(self, data):
        """The current program scene has changed."""
        print(f"{self.event_identifier}: {data}")


def version():
    print(req_cl.get_version())


def set_scene(scene, *args):
    req_cl.set_current_program_scene(scene)


if __name__ == "__main__":
    req_cl = obs.ReqClient()
    req_ev = obs.EventClient()
    observer = Observer(req_ev)

    keyboard.add_hotkey("1", set_scene, args=("START",))
    keyboard.add_hotkey("2", set_scene, args=("BRB",))
    keyboard.add_hotkey("3", set_scene, args=("END",))

    print("press ctrl+enter to quit")
    keyboard.wait("ctrl+enter")

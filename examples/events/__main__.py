import time

import obsws_python as obs


class Observer:
    def __init__(self):
        self._client = obs.EventClient()
        self._client.callback.register(
            [
                self.on_current_program_scene_changed,
                self.on_scene_created,
                self.on_input_mute_state_changed,
                self.on_exit_started,
            ]
        )
        print(f"Registered events: {self._client.callback.get()}")
        self.running = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._client.disconnect()

    def on_current_program_scene_changed(self, data):
        """The current program scene has changed."""
        print(f"Switched to scene {data.scene_name}")

    def on_scene_created(self, data):
        """A new scene has been created."""
        print(f"scene {data.scene_name} has been created")

    def on_input_mute_state_changed(self, data):
        """An input's mute state has changed."""
        print(f"{data.input_name} mute toggled")

    def on_exit_started(self, _):
        """OBS has begun the shutdown process."""
        print("OBS closing!")
        self.running = False


if __name__ == "__main__":
    with Observer() as observer:
        while observer.running:
            time.sleep(0.1)

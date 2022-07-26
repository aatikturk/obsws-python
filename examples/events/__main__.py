import obsstudio_sdk as obs


class Observer:
    def __init__(self, cl):
        self._cl = cl
        self._cl.callback.register(
            [
                self.on_current_program_scene_changed,
                self.on_scene_created,
                self.on_input_mute_state_changed,
                self.on_exit_started,
            ]
        )
        print(f"Registered events: {self._cl.callback.get()}")

    def on_current_program_scene_changed(self, data):
        """The current program scene has changed."""
        print(f"Switched to scene {data['sceneName']}")

    def on_scene_created(self, data):
        """A new scene has been created."""
        print(f"scene {data['sceneName']} has been created")

    def on_input_mute_state_changed(self, data):
        """An input's mute state has changed."""
        print(f"{data['inputName']} mute toggled")

    def on_exit_started(self, data):
        """OBS has begun the shutdown process."""
        print(f"OBS closing!")
        self._cl.unsubscribe()


if __name__ == "__main__":
    cl = obs.EventsClient()
    observer = Observer(cl)

    while cmd := input("<Enter> to exit\n"):
        if not cmd:
            break

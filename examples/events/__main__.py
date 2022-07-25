import obsstudio_sdk as obs


class Observer:
    def __init__(self, cl):
        self._cl = cl
        self._cl.callback.register(
            [self.on_current_program_scene_changed, self.on_exit_started]
        )
        print(f"Registered events: {self._cl.callback.get()}")

    def on_exit_started(self):
        print(f"OBS closing!")
        self._cl.unsubscribe()

    def on_current_program_scene_changed(self, data):
        print(f"Switched to scene {data['sceneName']}")


if __name__ == "__main__":
    cl = obs.EventsClient()
    observer = Observer(cl)

    while cmd := input("<Enter> to exit\n"):
        if not cmd:
            break

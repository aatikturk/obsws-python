import json
import time
from threading import Thread

from .baseclient import ObsClient
from .subject import Callback

"""
A class to interact with obs-websocket events
defined in official github repo
https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#events
"""


class EventsClient(object):
    DELAY = 0.001

    def __init__(self, **kwargs):
        self.base_client = ObsClient(**kwargs)
        self.base_client.authenticate()
        self.callback = Callback()

        self.running = True
        worker = Thread(target=self.trigger, daemon=True)
        worker.start()

    def trigger(self):
        """
        Continuously listen for events.

        Triggers a callback on event received.
        """
        while self.running:
            self.data = json.loads(self.base_client.ws.recv())
            event, data = (self.data["d"].get("eventType"), self.data["d"])
            self.callback.trigger(event, data)
            time.sleep(self.DELAY)

    def unsubscribe(self):
        """
        stop listening for events
        """
        self.running = False

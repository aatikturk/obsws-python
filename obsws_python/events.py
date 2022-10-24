import json
import logging
import time
from enum import IntEnum
from threading import Thread

from .baseclient import ObsClient
from .callback import Callback

"""
A class to interact with obs-websocket events
defined in official github repo
https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#events
"""

Subs = IntEnum(
    "Subs",
    "general config scenes inputs transitions filters outputs sceneitems mediainputs vendors ui",
    start=0,
)


class EventClient:
    logger = logging.getLogger("events.eventclient")
    DELAY = 0.001

    def __init__(self, **kwargs):
        defaultkwargs = {
            "subs": (
                (1 << Subs.general)
                | (1 << Subs.config)
                | (1 << Subs.scenes)
                | (1 << Subs.inputs)
                | (1 << Subs.transitions)
                | (1 << Subs.filters)
                | (1 << Subs.outputs)
                | (1 << Subs.sceneitems)
                | (1 << Subs.mediainputs)
                | (1 << Subs.vendors)
                | (1 << Subs.ui)
            )
        }
        kwargs = defaultkwargs | kwargs
        self.base_client = ObsClient(**kwargs)
        if self.base_client.authenticate():
            self.logger.info("Successfully identified client with the server")
        self.callback = Callback()
        self.subscribe()

    def subscribe(self):
        worker = Thread(target=self.trigger, daemon=True)
        worker.start()

    def trigger(self):
        """
        Continuously listen for events.

        Triggers a callback on event received.
        """
        self.running = True
        while self.running:
            event = json.loads(self.base_client.ws.recv())
            self.logger.debug(f"Event received {event}")
            type_, data = (
                event["d"].get("eventType"),
                event["d"].get("eventData"),
            )
            self.callback.trigger(type_, data if data else {})
            time.sleep(self.DELAY)

    def unsubscribe(self):
        """
        stop listening for events
        """
        self.running = False
        self.base_client.ws.close()

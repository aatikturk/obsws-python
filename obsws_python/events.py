import json
import logging
import time
from threading import Thread

from websocket import WebSocketTimeoutException

from .baseclient import ObsClient
from .callback import Callback
from .error import OBSSDKError, OBSSDKTimeoutError
from .subs import Subs

"""
A class to interact with obs-websocket events
defined in official github repo
https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#events
"""

logger = logging.getLogger(__name__)


class EventClient:
    DELAY = 0.001

    def __init__(self, **kwargs):
        self.logger = logger.getChild(self.__class__.__name__)
        defaultkwargs = {"subs": Subs.LOW_VOLUME}
        kwargs = defaultkwargs | kwargs
        self.base_client = ObsClient(**kwargs)
        try:
            success = self.base_client.authenticate()
            self.logger.info(
                f"Successfully identified {self} with the server using RPC version:{success['negotiatedRpcVersion']}"
            )
        except OBSSDKError as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            raise
        self.callback = Callback()
        self.subscribe()

    def __repr__(self):
        return type(
            self
        ).__name__ + "(host='{host}', port={port}, password='{password}', subs={subs}, timeout={timeout})".format(
            **self.base_client.__dict__,
        )

    def __str__(self):
        return type(self).__name__

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
            try:
                event = json.loads(self.base_client.ws.recv())
            except WebSocketTimeoutException as e:
                self.logger.exception(f"{type(e).__name__}: {e}")
                raise OBSSDKTimeoutError("Timeout while waiting for event") from e
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

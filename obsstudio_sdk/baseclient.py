import base64
import hashlib
import json
import time
from enum import IntEnum
from pathlib import Path
from random import randint

import tomllib
import websocket

Subs = IntEnum(
    "Subs",
    "general config scenes inputs transitions filters outputs sceneitems mediainputs vendors ui",
    start=0,
)


class ObsClient(object):
    DELAY = 0.001

    def __init__(self, **kwargs):
        defaultkwargs = {key: None for key in ["host", "port", "password"]}
        kwargs = defaultkwargs | kwargs
        for attr, val in kwargs.items():
            setattr(self, attr, val)
        if not (self.host and self.port and self.password):
            conn = self._conn_from_toml()
            self.host = conn["host"]
            self.port = conn["port"]
            self.password = conn["password"]

        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{self.host}:{self.port}")
        self.server_hello = json.loads(self.ws.recv())

    def _conn_from_toml(self):
        filepath = Path.cwd() / "config.toml"
        self._conn = dict()
        with open(filepath, "rb") as f:
            self._conn = tomllib.load(f)
        return self._conn["connection"]

    def authenticate(self):
        secret = base64.b64encode(
            hashlib.sha256(
                (
                    self.password + self.server_hello["d"]["authentication"]["salt"]
                ).encode()
            ).digest()
        )

        auth = base64.b64encode(
            hashlib.sha256(
                (
                    secret.decode()
                    + self.server_hello["d"]["authentication"]["challenge"]
                ).encode()
            ).digest()
        ).decode()

        all_non_high_volume = (
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

        payload = {
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "authentication": auth,
                "eventSubscriptions": all_non_high_volume,
            },
        }

        self.ws.send(json.dumps(payload))
        return self.ws.recv()

    def req(self, req_type, req_data=None):
        if req_data:
            payload = {
                "op": 6,
                "d": {
                    "requestType": req_type,
                    "requestId": randint(1, 1000),
                    "requestData": req_data,
                },
            }
        else:
            payload = {
                "op": 6,
                "d": {"requestType": req_type, "requestId": randint(1, 1000)},
            }
        self.ws.send(json.dumps(payload))
        response = json.loads(self.ws.recv())
        while "requestId" not in response["d"]:
            response = json.loads(self.ws.recv())
            time.sleep(self.DELAY)
        return response["d"]

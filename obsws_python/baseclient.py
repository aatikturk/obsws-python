import base64
import hashlib
import json
import logging
from pathlib import Path
from random import randint

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import websocket

from .error import OBSSDKError


class ObsClient:
    logger = logging.getLogger("baseclient.obsclient")

    def __init__(self, **kwargs):
        defaultkwargs = {
            **{key: None for key in ["host", "port", "password"]},
            "subs": 0,
        }
        kwargs = defaultkwargs | kwargs
        for attr, val in kwargs.items():
            setattr(self, attr, val)
        if not (self.host and self.port):
            conn = self._conn_from_toml()
            self.host = conn["host"]
            self.port = conn["port"]
            self.password = conn["password"]

        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{self.host}:{self.port}")
        self.server_hello = json.loads(self.ws.recv())

    def _conn_from_toml(self):
        filepath = Path.cwd() / "config.toml"
        with open(filepath, "rb") as f:
            conn = tomllib.load(f)
        return conn["connection"]

    def authenticate(self):
        payload = {
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "eventSubscriptions": self.subs,
            },
        }

        if "authentication" in self.server_hello["d"]:
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

            payload["d"]["authentication"] = auth

        self.ws.send(json.dumps(payload))
        try:
            response = json.loads(self.ws.recv())
            return response["op"] == 2
        except json.decoder.JSONDecodeError:
            raise OBSSDKError("failed to identify client with the server")

    def req(self, req_type, req_data=None):
        id = randint(1, 1000)
        self.logger.debug(f"Sending request with response id {id}")
        payload = {
            "op": 6,
            "d": {"requestType": req_type, "requestId": id},
        }
        if req_data:
            payload["d"]["requestData"] = req_data
        self.ws.send(json.dumps(payload))
        response = json.loads(self.ws.recv())
        self.logger.debug(f"Reponse received {response}")
        return response["d"]

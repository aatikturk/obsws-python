import base64
import hashlib
import json
import logging
from pathlib import Path
from random import randint
from typing import Optional

import websocket
from websocket import WebSocketTimeoutException

from .error import OBSSDKError, OBSSDKTimeoutError

logger = logging.getLogger(__name__)


class ObsClient:
    def __init__(self, **kwargs):
        self.logger = logger.getChild(self.__class__.__name__)
        defaultkwargs = {
            "host": "localhost",
            "port": 4455,
            "password": "",
            "subs": 0,
            "timeout": None,
        }
        if not any(key in kwargs for key in ("host", "port", "password")):
            kwargs |= self._conn_from_toml()
        kwargs = defaultkwargs | kwargs
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.logger.info(
            "Connecting with parameters: host='{host}' port={port} password='{password}' subs={subs} timeout={timeout}".format(
                **self.__dict__
            )
        )

        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(f"ws://{self.host}:{self.port}", timeout=self.timeout)
            self.server_hello = json.loads(self.ws.recv())
        except ValueError as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            raise
        except (ConnectionRefusedError, TimeoutError, WebSocketTimeoutException) as e:
            self.logger.exception(f"{type(e).__name__}: {e}")
            raise

    def _conn_from_toml(self) -> dict:
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib

        def get_filepath() -> Optional[Path]:
            """
            traverses a list of paths for a 'config.toml'
            returns the first config file found or None.
            """
            filepaths = [
                Path.cwd() / "config.toml",
                Path.home() / "config.toml",
                Path.home() / ".config" / "obsws-python" / "config.toml",
            ]
            for filepath in filepaths:
                if filepath.exists():
                    return filepath

        conn = {}
        if filepath := get_filepath():
            with open(filepath, "rb") as f:
                conn = tomllib.load(f)
            self.logger.info(f"loading config from {filepath}")
        return conn["connection"] if "connection" in conn else conn

    def authenticate(self):
        payload = {
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "eventSubscriptions": self.subs,
            },
        }

        if "authentication" in self.server_hello["d"]:
            if not self.password:
                raise OBSSDKError("authentication enabled but no password provided")
            secret = base64.b64encode(
                hashlib.sha256(
                    (
                        self.password + self.server_hello["d"]["authentication"]["salt"]
                    ).encode()
                ).digest()
            )

            auth = base64.b64encode(
                hashlib.sha256(
                    secret
                    + self.server_hello["d"]["authentication"]["challenge"].encode()
                ).digest()
            ).decode()

            payload["d"]["authentication"] = auth

        self.ws.send(json.dumps(payload))
        try:
            response = json.loads(self.ws.recv())
            if response["op"] != 2:
                raise OBSSDKError(
                    "failed to identify client with the server, expected response with OpCode 2"
                )
            return response["d"]
        except json.decoder.JSONDecodeError:
            raise OBSSDKError(
                "failed to identify client with the server, please check connection settings"
            )

    def req(self, req_type, req_data=None):
        payload = {
            "op": 6,
            "d": {"requestType": req_type, "requestId": randint(1, 1000)},
        }
        if req_data:
            payload["d"]["requestData"] = req_data
        self.logger.debug(f"Sending request {payload}")
        try:
            self.ws.send(json.dumps(payload))
            response = json.loads(self.ws.recv())
        except WebSocketTimeoutException as e:
            self.logger.exception(f"{type(e).__name__}: {e}")
            raise OBSSDKTimeoutError("Timeout while trying to send the request") from e
        self.logger.debug(f"Response received {response}")
        return response["d"]

import websocket
import json
import hashlib
import base64
from random import randint

class ObsClient(object):
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{self.host}:{self.port}")
        self.server_hello = json.loads(self.ws.recv())

    def authenticate(self):
        secret = base64.b64encode(
            hashlib.sha256(
                (self.password + self.server_hello['d']['authentication']['salt']).encode()).digest())
        
        auth = base64.b64encode(
             hashlib.sha256(
                 (secret.decode() + self.server_hello['d']['authentication']['challenge']).encode()).digest()).decode()
        
        payload = { "op":1, "d": {
            "rpcVersion": 1,
            "authentication": auth}
            }
        
        self.ws.send(json.dumps(payload))
        return self.ws.recv()

    def req(self, req_type, req_data=None):
        if req_data == None:
            payload = {
                "op": 6,
                "d": {
                    "requestType": req_type,
                    "requestId": randint(1, 1000)
                }
            }
        else:
            payload = {
                "op": 6,
                "d": {
                    "requestType": req_type,
                    "requestId": randint(1, 1000),
                    "requestData": req_data
                }
            }
        self.ws.send(json.dumps(payload))
        return json.loads(self.ws.recv())
        
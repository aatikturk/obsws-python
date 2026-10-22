import json
from unittest import mock

import obsws_python as obsws


class FakeWebSocket:
    """Replays server messages. A callable message answers the last request sent."""

    def __init__(self, messages):
        self.messages = list(messages)
        self.sent = []

    def connect(self, url, timeout=None):
        pass

    def send(self, payload):
        self.sent.append(json.loads(payload))

    def recv(self):
        message = self.messages.pop(0)
        if callable(message):
            message = message(self.sent[-1]["d"])
        return json.dumps(message)


def response(request_type, request_id, data):
    return {
        "op": 7,
        "d": {
            "requestType": request_type,
            "requestId": request_id,
            "requestStatus": {"result": True, "code": 100},
            "responseData": data,
        },
    }


class TestBaseClient:
    __test__ = True

    def test_response_to_another_request_is_not_returned(self):
        ws = FakeWebSocket(
            [
                {"op": 0, "d": {"obsWebSocketVersion": "5.5.0", "rpcVersion": 1}},
                {"op": 2, "d": {"negotiatedRpcVersion": 1}},
                # late response to an earlier request, such as one that timed out
                response("GetVersion", "1", {"obsVersion": "31.0.0"}),
                lambda req: response(
                    req["requestType"], req["requestId"], {"cpuUsage": 1.5}
                ),
            ]
        )
        with mock.patch("websocket.WebSocket", return_value=ws):
            cl = obsws.ReqClient(host="localhost", port=4455, password="")

        resp = cl.get_stats()
        assert resp.cpu_usage == 1.5

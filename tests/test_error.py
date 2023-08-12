import pytest

import obsws_python as obsws
from tests import req_cl


class TestErrors:
    __test__ = True

    def test_it_raises_an_obssdk_error_on_incorrect_password(self):
        bad_conn = {"host": "localhost", "port": 4455, "password": "incorrectpassword"}
        with pytest.raises(
            obsws.error.OBSSDKError,
            match="failed to identify client with the server, please check connection settings",
        ):
            obsws.ReqClient(**bad_conn)

    def test_it_raises_an_obssdk_error_if_auth_enabled_but_no_password_provided(self):
        bad_conn = {"host": "localhost", "port": 4455, "password": ""}
        with pytest.raises(
            obsws.error.OBSSDKError,
            match="authentication enabled but no password provided",
        ):
            obsws.ReqClient(**bad_conn)

    def test_it_raises_a_request_error_on_invalid_request(self):
        with pytest.raises(
            obsws.error.OBSSDKRequestError,
            match="Request SetCurrentProgramScene returned code 600. With message: No source was found by the name of `invalid`.",
        ) as exc_info:
            req_cl.set_current_program_scene("invalid")

        e = exc_info.value
        assert e.req_name == "SetCurrentProgramScene"
        assert e.code == 600

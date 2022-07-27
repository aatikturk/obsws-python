import pytest

from tests import req_cl


class TestRequests:
    __test__ = True

    def test_get_version(self):
        resp = req_cl.get_version()
        assert hasattr(resp, "obs_version")
        assert hasattr(resp, "obs_web_socket_version")

    @pytest.mark.parametrize(
        "scene",
        [
            ("START"),
            ("BRB"),
            ("END"),
        ],
    )
    def test_current_program_scene(self, scene):
        req_cl.set_current_program_scene(scene)
        resp = req_cl.get_current_program_scene()
        assert resp.current_program_scene_name == scene

    @pytest.mark.parametrize(
        "state",
        [
            (False),
            (True),
        ],
    )
    def test_studio_mode_enabled(self, state):
        req_cl.set_studio_mode_enabled(state)
        resp = req_cl.get_studio_mode_enabled()
        assert resp.studio_mode_enabled == state

    @pytest.mark.parametrize(
        "name,data",
        [
            ("val1", 3),
            ("val2", "hello"),
        ],
    )
    def test_persistent_data(self, name, data):
        req_cl.set_persistent_data("OBS_WEBSOCKET_DATA_REALM_PROFILE", name, data)
        resp = req_cl.get_persistent_data("OBS_WEBSOCKET_DATA_REALM_PROFILE", name)
        assert resp.slot_value == data

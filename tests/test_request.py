import time

import pytest

from tests import req_cl


class TestRequests:
    __test__ = True

    def test_get_version(self):
        resp = req_cl.get_version()
        assert "obsVersion" in resp
        assert "obsWebSocketVersion" in resp

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
        assert resp["currentProgramSceneName"] == scene

    @pytest.mark.parametrize(
        "state",
        [
            (False),
            (True),
        ],
    )
    def test_set_studio_mode_enabled_true(self, state):
        req_cl.set_studio_mode_enabled(state)
        resp = req_cl.get_studio_mode_enabled()
        assert resp["studioModeEnabled"] == state

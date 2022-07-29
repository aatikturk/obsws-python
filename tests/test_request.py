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

    def test_get_hot_key_list(self):
        resp = req_cl.get_hot_key_list()
        hotkey_list = [
            "OBSBasic.StartStreaming",
            "OBSBasic.StopStreaming",
            "OBSBasic.ForceStopStreaming",
            "OBSBasic.StartRecording",
            "OBSBasic.StopRecording",
            "OBSBasic.PauseRecording",
            "OBSBasic.UnpauseRecording",
            "OBSBasic.StartReplayBuffer",
            "OBSBasic.StopReplayBuffer",
            "OBSBasic.StartVirtualCam",
            "OBSBasic.StopVirtualCam",
            "OBSBasic.EnablePreview",
            "OBSBasic.DisablePreview",
            "OBSBasic.ShowContextBar",
            "OBSBasic.HideContextBar",
            "OBSBasic.TogglePreviewProgram",
            "OBSBasic.Transition",
            "OBSBasic.ResetStats",
            "OBSBasic.Screenshot",
            "OBSBasic.SelectedSourceScreenshot",
            "libobs.mute",
            "libobs.unmute",
            "libobs.push-to-mute",
            "libobs.push-to-talk",
            "libobs.mute",
            "libobs.unmute",
            "libobs.push-to-mute",
            "libobs.push-to-talk",
            "OBSBasic.SelectScene",
            "OBSBasic.SelectScene",
            "OBSBasic.SelectScene",
            "OBSBasic.SelectScene",
            "libobs.show_scene_item.Colour Source 2",
            "libobs.hide_scene_item.Colour Source 2",
            "libobs.show_scene_item.Colour Source 3",
            "libobs.hide_scene_item.Colour Source 3",
            "libobs.show_scene_item.Colour Source",
            "libobs.hide_scene_item.Colour Source",
            "OBSBasic.QuickTransition.1",
            "OBSBasic.QuickTransition.2",
            "OBSBasic.QuickTransition.3",
        ]
        assert all(x in resp.hotkeys for x in hotkey_list)

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

    def test_profile_list(self):
        req_cl.create_profile("test")
        resp = req_cl.get_profile_list()
        assert "test" in resp.profiles
        req_cl.remove_profile("test")
        resp = req_cl.get_profile_list()
        assert "test" not in resp.profiles

    def test_source_filter(self):
        req_cl.create_source_filter("START", "test", "color_key_filter_v2")
        resp = req_cl.get_source_filter_list("START")
        assert resp.filters == [
            {
                "filterEnabled": True,
                "filterIndex": 0,
                "filterKind": "color_key_filter_v2",
                "filterName": "test",
                "filterSettings": {},
            }
        ]
        req_cl.remove_source_filter("START", "test")

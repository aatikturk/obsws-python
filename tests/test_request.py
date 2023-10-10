import pytest

from tests import req_cl


class TestRequests:
    __test__ = True

    def test_get_version(self):
        resp = req_cl.get_version()
        assert hasattr(resp, "obs_version")
        assert hasattr(resp, "obs_web_socket_version")

    def test_get_hot_key_list(self):
        resp = req_cl.get_hot_key_list()
        obsbasic_hotkey_list = [
            "OBSBasic.SelectScene",
            "OBSBasic.QuickTransition.1",
            "OBSBasic.QuickTransition.2",
            "OBSBasic.QuickTransition.3",
            "OBSBasic.StartStreaming",
            "OBSBasic.StopStreaming",
            "OBSBasic.ForceStopStreaming",
            "OBSBasic.StartRecording",
            "OBSBasic.StopRecording",
            "OBSBasic.PauseRecording",
            "OBSBasic.UnpauseRecording",
            "OBSBasic.SplitFile",
            "OBSBasic.StartReplayBuffer",
            "OBSBasic.StopReplayBuffer",
            "OBSBasic.StartVirtualCam",
            "OBSBasic.StopVirtualCam",
            "OBSBasic.EnablePreview",
            "OBSBasic.DisablePreview",
            "OBSBasic.EnablePreviewProgram",
            "OBSBasic.DisablePreviewProgram",
            "OBSBasic.ShowContextBar",
            "OBSBasic.HideContextBar",
            "OBSBasic.Transition",
            "OBSBasic.ResetStats",
            "OBSBasic.Screenshot",
            "OBSBasic.SelectedSourceScreenshot",
        ]
        assert all(x in resp.hotkeys for x in obsbasic_hotkey_list)

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

    def test_stream_service_settings(self):
        settings = {
            "server": "rtmp://addressofrtmpserver",
            "key": "live_myvery_secretkey",
        }
        req_cl.set_stream_service_settings(
            "rtmp_common",
            settings,
        )
        resp = req_cl.get_stream_service_settings()
        assert resp.stream_service_type == "rtmp_common"
        assert resp.stream_service_settings == {
            "server": "rtmp://addressofrtmpserver",
            "key": "live_myvery_secretkey",
        }

    @pytest.mark.parametrize(
        "scene",
        [
            ("START_TEST"),
            ("BRB_TEST"),
            ("END_TEST"),
        ],
    )
    def test_current_program_scene(self, scene):
        req_cl.set_current_program_scene(scene)
        resp = req_cl.get_current_program_scene()
        assert resp.current_program_scene_name == scene

    def test_input_list(self):
        req_cl.create_input(
            "START_TEST", "test", "color_source_v3", {"color": 4294945535}, True
        )
        resp = req_cl.get_input_list()
        assert {
            "inputKind": "color_source_v3",
            "inputName": "test",
            "unversionedInputKind": "color_source",
        } in resp.inputs
        resp = req_cl.get_input_settings("test")
        assert resp.input_kind == "color_source_v3"
        assert resp.input_settings == {"color": 4294945535}
        req_cl.remove_input("test")

    def test_source_filter(self):
        req_cl.create_source_filter("START_TEST", "test", "color_key_filter_v2")
        resp = req_cl.get_source_filter_list("START_TEST")
        assert resp.filters == [
            {
                "filterEnabled": True,
                "filterIndex": 0,
                "filterKind": "color_key_filter_v2",
                "filterName": "test",
                "filterSettings": {},
            }
        ]
        req_cl.remove_source_filter("START_TEST", "test")

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

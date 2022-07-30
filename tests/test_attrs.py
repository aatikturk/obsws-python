from tests import req_cl


class TestAttrs:
    __test__ = True

    def test_get_version_attrs(self):
        resp = req_cl.get_version()
        assert resp.attrs() == [
            "available_requests",
            "obs_version",
            "obs_web_socket_version",
            "platform",
            "platform_description",
            "rpc_version",
            "supported_image_formats",
        ]

    def test_get_current_program_scene_attrs(self):
        resp = req_cl.get_current_program_scene()
        assert resp.attrs() == ["current_program_scene_name"]

    def test_get_transition_kind_list_attrs(self):
        resp = req_cl.get_transition_kind_list()
        assert resp.attrs() == ["transition_kinds"]

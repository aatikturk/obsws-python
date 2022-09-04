import obsws_python as obs

req_cl = obs.ReqClient()


def setup_module():
    req_cl.create_scene("START_TEST")
    req_cl.create_scene("BRB_TEST")
    req_cl.create_scene("END_TEST")


def teardown_module():
    req_cl.remove_scene("START_TEST")
    req_cl.remove_scene("BRB_TEST")
    req_cl.remove_scene("END_TEST")
    req_cl.base_client.ws.close()

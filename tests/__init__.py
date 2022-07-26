import obsstudio_sdk as obs

req_cl = obs.ReqClient()


def setup_module():
    pass


def teardown_module():
    req_cl.base_client.ws.close()

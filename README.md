# obs_sdk

### A Python SDK for OBS Studio WebSocket v5.0

This is a wrapper around OBS Websocket.
Not all endpoints in the official documentation are implemented. But all endpoints in the Requests section is implemented. You can find the relevant document using below link.
[obs-websocket github page](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#Requests)

## Requirements

-   [OBS Studio](https://obsproject.com/)
-   [OBS Websocket v5 Plugin](https://github.com/obsproject/obs-websocket/releases/tag/5.0.0)
-   Python 3.11 or greater

### How to install using pip

```
pip install obsstudio-sdk
```

### How to Use

-   Load connection info from toml config. A valid `config.toml` might look like this:

```toml
[connection]
host = "localhost"
port = 4455
password = "mystrongpass"
```

It should be placed next to your `__main__.py` file.

Otherwise:

-   Import and start using
    Parameters are as follows:
    host: obs websocket server
    port: port to access server
    password: obs websocket server password

```
>>>from obsstudio_sdk.reqs import ReqClient
>>>
>>>client = ReqClient('192.168.1.1', 4444, 'somepassword')
```

Now you can make calls to OBS

Example: Toggle the mute state of your Mic input

```
>>>cl.ToggleInputMute('Mic/Aux')
>>>

```

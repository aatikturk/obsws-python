[![PyPI version](https://badge.fury.io/py/obsws-python.svg)](https://badge.fury.io/py/obsws-python)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/aatikturk/obsstudio_sdk/blob/main/LICENSE)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# A Python SDK for OBS Studio WebSocket v5.0

Not all endpoints in the official documentation are implemented.

## Requirements

- [OBS Studio](https://obsproject.com/)
- [OBS Websocket v5 Plugin](https://github.com/obsproject/obs-websocket/releases/tag/5.0.0)
  - With the release of OBS Studio version 28, Websocket plugin is included by default. But it should be manually installed for earlier versions of OBS.
- Python 3.9 or greater

### How to install using pip

```
pip install obsws-python
```

### How to Use

By default the clients connect with parameters:

- `host`: "localhost"
- `port`: 4455
- `password`: ""
- `timeout`: None

You may override these parameters by storing them in a toml config file or passing them as keyword arguments.

Order of precedence: keyword arguments then config file then default values.

#### `config file`

A valid `config.toml` might look like this:

```toml
[connection]
host = "localhost"
port = 4455
password = "mystrongpass"
```

It should be placed in your user home directory.

#### Otherwise:

Example `__main__.py`:

```python
import obsws_python as obs

# pass conn info if not in config.toml
cl = obs.ReqClient(host='localhost', port=4455, password='mystrongpass', timeout=3)

# Toggle the mute state of your Mic input
cl.toggle_input_mute('Mic/Aux')
```

### Requests

Method names for requests match the API calls but snake cased. If a successful call is made with the Request client and the response is expected to contain fields then a response object will be returned. You may then access the response fields as class attributes. They will be snake cased.

example:

```python
# load conn info from config.toml
cl = obs.ReqClient()

# GetVersion, returns a response object
resp = cl.get_version()
# Access it's field as an attribute
print(f"OBS Version: {resp.obs_version}")


# SetCurrentProgramScene
cl.set_current_program_scene("BRB")
```

#### `send(param, data=None, raw=False)`

If you prefer to work with the JSON data directly the {ReqClient}.send() method accepts an argument, `raw`. If set to True the raw response data will be returned, instead of a response object.

example:

```python
resp = cl_req.send("GetVersion", raw=True)

print(f"response data: {resp}")
```

For a full list of requests refer to [Requests][obsws-reqs]

### Events

When registering a callback function use the name of the expected API event in snake case form, prepended with "on\_".

example:

```python
# load conn info from config.toml
cl = obs.EventClient()

def on_scene_created(data):
    ...

# SceneCreated
cl.callback.register(on_scene_created)

def on_input_mute_state_changed(data):
    ...

# InputMuteStateChanged
cl.callback.register(on_input_mute_state_changed)

# returns a list of currently registered events
print(cl.callback.get())

# You may also deregister a callback
cl.callback.deregister(on_input_mute_state_changed)
```

`register(fns)` and `deregister(fns)` accept both single functions and lists of functions.

For a full list of events refer to [Events][obsws-events]

### Attributes

For both request responses and event data you may inspect the available attributes using `attrs()`.

example:

```python
resp = cl.get_version()
print(resp.attrs())

def on_scene_created(data):
    print(data.attrs())
```

### Errors

- `OBSSDKError`: Base error class.
- `OBSSDKTimeoutError`: Raised if a timeout occurs during sending/receiving a request or receiving an event
- `OBSSDKRequestError`: Raised when a request returns an error code.
  - The following attributes are available:
    - `req_name`: name of the request.
    - `code`: request status code.
  - For a full list of status codes refer to [Codes][obsws-codes]

### Logging

If you want to see the raw messages simply set log level to DEBUG

example:

```python
import obsws_python as obs
import logging


logging.basicConfig(level=logging.DEBUG)
...
```

### Tests

Install [hatch][hatch-install] and then:

```
hatch test
```

### Official Documentation

For the full documentation:

- [OBS Websocket SDK][obsws-pro]


[obsws-reqs]: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#requests
[obsws-events]: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#events
[obsws-codes]: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#requeststatus
[obsws-pro]: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#obs-websocket-501-protocol
[hatch-install]: https://hatch.pypa.io/latest/install/

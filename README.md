[![PyPI version](https://badge.fury.io/py/obsstudio-sdk.svg)](https://badge.fury.io/py/obsstudio-sdk)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/aatikturk/obsstudio_sdk/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# A Python SDK for OBS Studio WebSocket v5.0

This is a wrapper around OBS Websocket.
Not all endpoints in the official documentation are implemented.

## Requirements

-   [OBS Studio](https://obsproject.com/)
-   [OBS Websocket v5 Plugin](https://github.com/obsproject/obs-websocket/releases/tag/5.0.0)
-   Python 3.11 or greater

### How to install using pip

```
pip install obsstudio-sdk
```

### How to Use

Load connection info from toml config. A valid `config.toml` might look like this:

```toml
[connection]
host = "localhost"
port = 4455
password = "mystrongpass"
```

It should be placed next to your `__main__.py` file.

#### Otherwise:

Import and start using, keyword arguments are as follows:

-   `host`: obs websocket server
-   `port`: port to access server
-   `password`: obs websocket server password

Example `__main__.py`:

```python
import obsstudio_sdk as obs

# pass conn info if not in config.toml
cl = obs.ReqClient(host='localhost', port=4455, password='mystrongpass')

# Toggle the mute state of your Mic input
cl.toggle_input_mute('Mic/Aux')
```

### Requests

Method names for requests match the API calls but snake cased.

example:

```python
cl = ReqClient()

# GetVersion
resp = cl.get_version()

# SetCurrentProgramScene
cl.set_current_program_scene()
```

For a full list of requests refer to [Requests](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#requests)

### Events

When registering a function callback use the name of the expected API event in snake case form.

example:

```python
cl = EventClient()

def scene_created(data):
    ...

# SceneCreated
cl.callback.register(scene_created)

def input_mute_state_changed(data):
    ...

# InputMuteStateChanged
cl.callback.register(input_mute_state_changed)

# returns a list of currently registered events
print(cl.callback.get())

# You may also deregister a callback
cl.callback.deregister(input_mute_state_changed)
```

`register(fns)` and `deregister(fns)` accept both single functions and lists of functions.

For a full list of events refer to [Events](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#events)

### Attributes

For both request responses and event data you may inspect the available attributes using `attrs()`.

example:

```python
resp = cl.get_version()
print(resp.attrs())

def scene_created(data):
    print(data.attrs())
```

### Errors

If a request fails an `OBSSDKError` will be raised with a status code.

For a full list of status codes refer to [Codes](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#requeststatus)

### Tests

First install development dependencies:

`pip install -e .['dev']`

To run all tests:

```
pytest -v
```

### Official Documentation

For the full documentation:

-   [OBS Websocket SDK](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#obs-websocket-501-protocol)

# obs_sdk
### A Python SDK for OBS Studio WebSocket v5.0

This is a wrapper around OBS Websocket. 
Not all endpoints in the official documentation are implemented. But all endpoints in the Requests section is implemented. You can find the relevant document using below link.
[obs-websocket github page](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#Requests)

### How to install using pip

```
pip install obsstudio-sdk
```


### How to Use

* Import and start using
  Required parameters are as follows:
    host:       obs websocket server
    port:       port to access server
    password:   obs websocket server password

```
>>>from obsstudio_sdk.reqs import ReqClient
>>>
>>>client = ReqClient('192.168.1.1', 4444, 'somepassword')
```

Now you can make calls to OBS 

Example:  Toggle the mute state of your Mic input

```
>>>cl.ToggleInputMute('Mic/Aux')
>>>

```
## About

Registers a list of callback functions to hook into OBS events.

## Use

Simply run the code and trigger the events, press `<Enter>` to exit.

This example assumes the existence of a `config.toml`, placed in your user home directory:

```toml
[connection]
host = "localhost"
port = 4455
password = "mystrongpass"
```

Closing OBS ends the script.

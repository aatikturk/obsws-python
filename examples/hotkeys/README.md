## About

Sets up some hotkeys to trigger certain actions. Registers a callback function to notify of scene switch event.

Requires [Python Keyboard library](https://github.com/boppreh/keyboard).

## Use

Simply run the code and press the assigned hotkeys. Press `ctrl+enter` to exit.

This example assumes the existence of a `config.toml`, placed in your user home directory:

```toml
[connection]
host = "localhost"
port = 4455
password = "mystrongpass"
```

It also assumes the existence of scenes named `START`, `BRB` and `END`.

import re
from dataclasses import dataclass


def to_camel_case(s):
    s = "".join(word.title() for word in s.split("_"))
    return s[2:]


def to_snake_case(s):
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
    return f"{s}"


def as_dataclass(identifier, data):
    return dataclass(
        type(
            f"{identifier}Dataclass",
            (),
            {**{to_snake_case(k): v for k, v in data.items()}},
        )
    )

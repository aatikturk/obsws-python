import re
from dataclasses import dataclass


def to_camel_case(s):
    return "".join(word.title() for word in s.split("_"))


def to_snake_case(s):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def as_dataclass(identifier, data):
    def attrs():
        return list(to_snake_case(k) for k in data.keys())

    return dataclass(
        type(
            f"{identifier}Dataclass",
            (),
            {
                "attrs": attrs,
                **{to_snake_case(k): v for k, v in data.items()},
            },
        )
    )

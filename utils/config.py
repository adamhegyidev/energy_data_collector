from pathlib import Path

import yaml


CONFIG_DIR = Path(
    "config"
)


def load_yaml(filename):

    path = CONFIG_DIR / filename

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return yaml.safe_load(file)


def load_sources():

    return load_yaml(
        "sources.yaml"
    )


def get_mavir_sources():

    config = load_sources()

    return config.get(
        "mavir",
        {}
    )
"""Carga config.yaml y lo expone como un dict de Python."""
import pathlib
import yaml

CONFIG_PATH = pathlib.Path(__file__).resolve().parent.parent / "config.yaml"


def load_config(path: pathlib.Path = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

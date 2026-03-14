import json
from copy import deepcopy
from .config import SCHEMA_PATH

def load_schema_template() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def new_record() -> dict:
    return deepcopy(load_schema_template())

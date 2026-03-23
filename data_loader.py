import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str):
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_modules():
    return load_json("module_map.json")


def load_defects():
    return load_json("defect_log.json")


def load_tests():
    return load_json("test_cases.json")
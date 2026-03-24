from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from .storage import FINAL_DATA_PATH, REPO_ROOT


SCHEMA_PATH = REPO_ROOT / "packages" / "schema" / "shop.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def build_validator() -> Draft202012Validator:
    return Draft202012Validator(load_schema(), format_checker=FormatChecker())


def validate_dataset_payload(payload: dict) -> None:
    validator = build_validator()
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))

    if not errors:
        return

    error = errors[0]
    location = " -> ".join(str(part) for part in error.path) or "<root>"
    raise ValidationError(f"{location}: {error.message}")


def validate_dataset_file(path: Path = FINAL_DATA_PATH) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset_payload(payload)

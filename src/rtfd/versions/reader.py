"""Reads and validates the single PySpark/Spark/Hadoop version file."""

import re
import tomllib
from dataclasses import dataclass, fields
from pathlib import Path

from rtfd.versions.errors import (
    VersionFileFormatError,
    VersionFileNotFoundError,
    VersionMismatchError,
)

# src/rtfd/versions/reader.py -> the repository root is three levels above this file's directory.
DEFAULT_VERSION_FILE = Path(__file__).resolve().parents[3] / "config" / "spark_versions.toml"

_VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


@dataclass(frozen=True)
class VersionPin:
    pyspark: str
    spark: str
    hadoop: str


def _major_minor(version: str) -> tuple[int, int]:
    major, minor, _ = version.split(".")
    return int(major), int(minor)


def validate_pin(pin: VersionPin) -> None:
    """Raise VersionMismatchError unless PySpark and Spark share major.minor."""
    if _major_minor(pin.pyspark) != _major_minor(pin.spark):
        raise VersionMismatchError(
            f"PySpark version {pin.pyspark} and Spark version {pin.spark} "
            "must share the same major.minor version"
        )


def read_version_pin(path: Path | str | None = None) -> VersionPin:
    """Read, validate and return the version pin.

    Uses the repository's config/spark_versions.toml when no path is given.
    Every failure raises a VersionPinError subclass; no default is ever returned.
    """
    file_path = Path(path) if path is not None else DEFAULT_VERSION_FILE
    if not file_path.is_file():
        raise VersionFileNotFoundError(f"Version file not found: {file_path}")

    try:
        with file_path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise VersionFileFormatError(f"Malformed version file {file_path}: {exc}") from exc

    expected = [f.name for f in fields(VersionPin)]
    missing = [key for key in expected if key not in data]
    if missing:
        raise VersionFileFormatError(f"Version file {file_path} is missing keys: {missing}")
    unknown = sorted(key for key in data if key not in expected)
    if unknown:
        raise VersionFileFormatError(f"Version file {file_path} has unknown keys: {unknown}")

    for key in expected:
        value = data[key]
        if not isinstance(value, str):
            raise VersionFileFormatError(
                f"Version file {file_path}: '{key}' must be a string, got {type(value).__name__}"
            )
        if not _VERSION_PATTERN.fullmatch(value):
            raise VersionFileFormatError(
                f"Version file {file_path}: '{key}' = {value!r} is not a MAJOR.MINOR.PATCH version"
            )

    pin = VersionPin(**{key: data[key] for key in expected})
    validate_pin(pin)
    return pin

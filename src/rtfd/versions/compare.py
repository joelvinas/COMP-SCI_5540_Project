"""Pure comparison of environment-reported versions against the pin."""

from dataclasses import dataclass
from typing import Literal

from rtfd.versions.reader import VersionPin

Component = Literal["pyspark", "spark", "hadoop"]


@dataclass(frozen=True)
class Mismatch:
    component: Component
    expected: str
    actual: str


@dataclass(frozen=True)
class ComparisonResult:
    matches: bool
    mismatches: tuple[Mismatch, ...]


def compare_versions(
    expected: VersionPin,
    reported_pyspark: str,
    reported_spark: str,
    reported_hadoop: str,
) -> ComparisonResult:
    """Compare reported versions to the pin by exact string match per component.

    Mismatches are listed in the fixed order pyspark, spark, hadoop.
    """
    pairs: tuple[tuple[Component, str, str], ...] = (
        ("pyspark", expected.pyspark, reported_pyspark),
        ("spark", expected.spark, reported_spark),
        ("hadoop", expected.hadoop, reported_hadoop),
    )
    mismatches = tuple(Mismatch(c, exp, act) for c, exp, act in pairs if exp != act)
    return ComparisonResult(matches=not mismatches, mismatches=mismatches)

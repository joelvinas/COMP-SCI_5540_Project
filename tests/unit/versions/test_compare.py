import dataclasses

import pytest

from rtfd.versions import Mismatch, VersionPin, compare_versions

PIN = VersionPin("3.5.1", "3.5.1", "3.4.0")


# Row 5: verification compares reported versions
def test_matching_versions_match():
    result = compare_versions(PIN, "3.5.1", "3.5.1", "3.4.0")
    assert result.matches is True
    assert result.mismatches == ()


def test_differing_spark_listed():
    result = compare_versions(PIN, "3.5.1", "3.4.2", "3.4.0")
    assert result.matches is False
    assert result.mismatches == (Mismatch("spark", "3.5.1", "3.4.2"),)


def test_patch_level_mismatch_is_mismatch():
    result = compare_versions(PIN, "3.5.4", "3.5.1", "3.4.0")
    assert result.mismatches == (Mismatch("pyspark", "3.5.1", "3.5.4"),)


def test_multiple_mismatches_in_fixed_order():
    result = compare_versions(PIN, "3.4.0", "3.4.0", "3.3.6")
    assert [m.component for m in result.mismatches] == ["pyspark", "spark", "hadoop"]
    assert result.matches is False


def test_empty_reported_value_is_mismatch():
    result = compare_versions(PIN, "3.5.1", "", "3.4.0")
    assert result.mismatches == (Mismatch("spark", "3.5.1", ""),)


def test_inputs_not_mutated_and_result_frozen():
    result = compare_versions(PIN, "3.5.1", "3.5.1", "3.4.0")
    assert PIN == VersionPin("3.5.1", "3.5.1", "3.4.0")
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.matches = False

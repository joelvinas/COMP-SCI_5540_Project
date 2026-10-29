import pytest

from rtfd.versions import (
    DEFAULT_VERSION_FILE,
    VersionFileFormatError,
    VersionFileNotFoundError,
    VersionMismatchError,
    VersionPin,
    read_version_pin,
)


# Row 1: single source of the pair
def test_reads_temporary_file_values(write_version_file, pin_text):
    path = write_version_file(pin_text("3.4.2", "3.4.2", "3.3.6"))
    assert read_version_pin(path) == VersionPin("3.4.2", "3.4.2", "3.3.6")


def test_accepts_str_path(write_version_file, pin_text):
    path = write_version_file(pin_text())
    assert read_version_pin(str(path)).spark == "3.5.1"


def test_path_with_spaces(tmp_path, pin_text):
    folder = tmp_path / "dir with spaces"
    folder.mkdir()
    path = folder / "my versions.toml"
    path.write_text(pin_text(), encoding="utf-8")
    assert read_version_pin(path).hadoop == "3.4.0"


# Row 2: default pair
def test_default_file_is_repo_config_and_cwd_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert DEFAULT_VERSION_FILE.is_absolute()
    assert DEFAULT_VERSION_FILE.parent.name == "config"
    pin = read_version_pin()
    assert pin.pyspark.split(".")[:2] == ["3", "5"]
    assert pin.spark.split(".")[:2] == ["3", "5"]
    assert pin.hadoop == "3.4.0"


# Row 3: re-pin by file edit only
def test_repin_by_file_edit_only(write_version_file, pin_text):
    path = write_version_file(pin_text("3.5.1", "3.5.1", "3.4.0"))
    assert read_version_pin(path).spark == "3.5.1"
    path.write_text(pin_text("3.4.2", "3.4.2", "3.3.6"), encoding="utf-8")
    assert read_version_pin(path) == VersionPin("3.4.2", "3.4.2", "3.3.6")


# Row 4: mismatched pair rejected
def test_mismatched_pair_names_both_versions(write_version_file, pin_text):
    path = write_version_file(pin_text("3.5.1", "4.2.0"))
    with pytest.raises(VersionMismatchError) as exc:
        read_version_pin(path)
    assert "3.5.1" in str(exc.value)
    assert "4.2.0" in str(exc.value)


def test_differing_patch_is_valid_pair(write_version_file, pin_text):
    path = write_version_file(pin_text("3.5.1", "3.5.4"))
    assert read_version_pin(path).spark == "3.5.4"


def test_major_minor_compared_as_integers(write_version_file, pin_text):
    path = write_version_file(pin_text("3.5.1", "3.10.0"))
    with pytest.raises(VersionMismatchError):
        read_version_pin(path)
    path.write_text(pin_text("3.10.1", "3.10.0"), encoding="utf-8")
    assert read_version_pin(path).pyspark == "3.10.1"


# Row 6: missing or malformed version file
def test_missing_file_raises(tmp_path):
    with pytest.raises(VersionFileNotFoundError):
        read_version_pin(tmp_path / "nope.toml")


def test_directory_as_path_raises(tmp_path):
    with pytest.raises(VersionFileNotFoundError):
        read_version_pin(tmp_path)


def test_unparseable_toml_raises(write_version_file):
    with pytest.raises(VersionFileFormatError):
        read_version_pin(write_version_file("pyspark = = ["))


def test_empty_file_raises(write_version_file):
    with pytest.raises(VersionFileFormatError):
        read_version_pin(write_version_file(""))


def test_missing_key_raises(write_version_file):
    with pytest.raises(VersionFileFormatError, match="hadoop"):
        read_version_pin(write_version_file('pyspark = "3.5.1"\nspark = "3.5.1"\n'))


def test_unknown_key_raises(write_version_file, pin_text):
    with pytest.raises(VersionFileFormatError, match="scala"):
        read_version_pin(write_version_file(pin_text() + 'scala = "2.12.18"\n'))


def test_non_string_value_raises(write_version_file):
    body = 'pyspark = 3.5\nspark = "3.5.1"\nhadoop = "3.4.0"\n'
    with pytest.raises(VersionFileFormatError, match="pyspark"):
        read_version_pin(write_version_file(body))


@pytest.mark.parametrize("bad", ["", "3.5", "3.5.x", "v3.5.1", "3.5.1-SNAPSHOT", "3.5.1 ", "3..1"])
def test_invalid_version_syntax_raises(write_version_file, pin_text, bad):
    with pytest.raises(VersionFileFormatError):
        read_version_pin(write_version_file(pin_text(spark=bad)))
    with pytest.raises(VersionFileFormatError):
        read_version_pin(write_version_file(pin_text(hadoop=bad)))

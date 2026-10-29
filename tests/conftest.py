import pytest


@pytest.fixture
def write_version_file(tmp_path):
    """Return a factory that writes raw text to a temporary version file."""

    def _write(content: str, name: str = "spark_versions.toml"):
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    return _write


@pytest.fixture
def pin_text():
    """Return a factory that renders a version file body."""

    def _render(pyspark="3.5.1", spark="3.5.1", hadoop="3.4.0"):
        return f'pyspark = "{pyspark}"\nspark = "{spark}"\nhadoop = "{hadoop}"\n'

    return _render

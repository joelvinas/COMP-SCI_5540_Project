"""Exceptions raised by the version pin reader."""


class VersionPinError(Exception):
    """Base class for all version pin errors."""


class VersionFileNotFoundError(VersionPinError):
    """The version file does not exist or is not a regular file."""


class VersionFileFormatError(VersionPinError):
    """The version file is unparseable, incomplete or holds invalid values."""


class VersionMismatchError(VersionPinError):
    """PySpark and Spark do not share the same major.minor version."""

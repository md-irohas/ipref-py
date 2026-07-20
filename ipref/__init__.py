from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ipref")
except PackageNotFoundError:  # pragma: no cover
    # package is not installed (e.g. run from a source tree)
    __version__ = "0.0.0"

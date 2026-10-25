from importlib import import_module
from types import ModuleType


class MissingDependencyError(ImportError):
    def __init__(self, package_name: str):
        self.package_name = package_name
        super().__init__(
            f"This file format requires the '{package_name}' package. "
            f"Install it with: python -m pip install {package_name}"
        )


def load_optional_dependency(module_name: str, package_name: str) -> ModuleType:
    try:
        return import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name is None:
            raise
        raise MissingDependencyError(package_name) from error

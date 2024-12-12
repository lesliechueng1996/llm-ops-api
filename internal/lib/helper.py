from importlib import import_module
from typing import Any


def dynamic_import(module_name: str, symbol_name: str) -> Any:
    module = import_module(module_name)
    return getattr(module, symbol_name)

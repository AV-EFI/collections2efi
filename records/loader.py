import functools
import importlib
import os
import tomllib


def _load_record_definitions():
    definitions_file = os.path.join(
        os.path.dirname(__file__), "record_definitions.toml"
    )
    with open(definitions_file, "rb") as f:
        definitions = tomllib.load(f)

    return definitions


def _validate_complex_mappings(definitions):
    for record_type, record_def in definitions.items():
        if record_type == "efi_classes":
            continue
        if "complex" in record_def:
            for complex_mapping in record_def["complex"]:
                attr = complex_mapping["attribute"]
                location = complex_mapping["location"]

                module_path = f"records.{location}.{attr}"

                try:
                    module = importlib.import_module(module_path)
                    if not hasattr(module, attr):
                        raise AttributeError(
                            f"Function '{attr}' not found in module '{module_path}' for record type '{record_type}'."
                        )
                except ImportError:
                    raise ImportError(
                        f"Module '{module_path}' not found for complex mapping '{attr}' in record type '{record_type}'."
                    )


@functools.lru_cache(maxsize=None)
def get_record_definitions():
    definitions = _load_record_definitions()
    _validate_complex_mappings(definitions)
    return definitions

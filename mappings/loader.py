import functools
import os
import tomllib

from avefi_schema import model as efi


@functools.lru_cache(maxsize=None)
def _load_and_resolve_mappings():
    mappings_file = os.path.join(os.path.dirname(__file__), "mappings.toml")
    with open(mappings_file, "rb") as f:
        raw_mappings = tomllib.load(f)

    resolved_enum_mappings = {}
    for enum_name, enum_mapping in raw_mappings.items():
        try:
            efi_enum_class = getattr(efi, enum_name)
        except AttributeError:
            raise AttributeError(
                f"Enum {enum_name} does not exist in efi schema, but is present in mappings.toml"
            )

        resolved_enum_mapping = {}
        for collections_name, efi_name in enum_mapping.items():
            try:
                resolved_enum_mapping[collections_name] = getattr(
                    efi_enum_class, efi_name
                )
            except AttributeError:
                raise AttributeError(
                    f"Mapping value {efi_name} of enum {enum_name} does not exist in efi schema"
                )
        resolved_enum_mappings[enum_name] = resolved_enum_mapping

    return resolved_enum_mappings


def get_mapping(name):
    all_mappings = _load_and_resolve_mappings()
    try:
        return all_mappings[name]
    except KeyError:
        raise KeyError(f"Mapping {name} not found")

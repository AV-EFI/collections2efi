import importlib
import inspect

from avefi_schema import model as efi

from collections2efi.loader import get_record_definitions
from collections2efi.record import Record
from collections2efi.record_type.base.utils import get_mapped_enum_value
from collections2efi.repositories import PeopleRepo, ThesauRepo


class Translator:
    def __init__(
        self,
        people_repo: PeopleRepo,
        thesau_repo: ThesauRepo,
    ):
        self.all_definitions = get_record_definitions()
        self.people_repo = people_repo
        self.thesau_repo = thesau_repo

    def translate(self, record: Record):
        record_type = record.xml.get_first(
            "record_type/value[@lang='neutral']/text()"
        ).lower()

        definition = self.all_definitions[record_type]
        efi_class_name = self.all_definitions["efi_classes"].get(record_type)
        if not efi_class_name:
            raise ValueError(
                f"EFI class mapping for record type '{record_type}' not found."
            )
        efi_class = getattr(efi, efi_class_name)
        attributes = {}

        if "simple" in definition:
            for attr, mapping in definition["simple"].items():
                value = record.xml.get_first(mapping["xpath"])
                if value is None:
                    continue
                attributes[attr] = get_mapped_enum_value(mapping["enum"], value)

        if "complex" in definition:
            for complex_mapping in definition["complex"]:
                attr = complex_mapping["attribute"]
                location = complex_mapping["location"]

                module_path = f"collections2efi.record_type.{location}.{attr}"
                module = importlib.import_module(module_path)
                func = getattr(module, attr)

                sig = inspect.signature(func)
                kwargs = {}
                if "xml" in sig.parameters:
                    kwargs["xml"] = record.xml
                if "people_repo" in sig.parameters:
                    kwargs["people_repo"] = self.people_repo
                if "thesau_repo" in sig.parameters:
                    kwargs["thesau_repo"] = self.thesau_repo

                attributes[attr] = func(**kwargs)

        return efi_class(**attributes)

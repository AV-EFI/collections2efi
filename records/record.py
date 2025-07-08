import importlib

from avefi_schema import model as efi

from records.loader import get_record_definitions
from records.utils import get_mapped_enum_value


class XMLAccessor:
    def __init__(self, xml_element):
        self._element = xml_element

    def get_first(self, xpath_expression):
        elements = self._element.xpath(xpath_expression)

        return elements[0] if elements else None

    def get_all(self, xpath_expression):
        elements = self._element.xpath(xpath_expression)

        if xpath_expression.endswith("/text()"):
            return elements

        return [XMLAccessor(el) for el in elements]

    def __getattr__(self, name):
        return getattr(self._element, name)

    def __repr__(self):
        return f"<XMLAccessor wrapping {self._element!r}>"


class Record:
    def __init__(self, record_type: str, xml_element):
        self.record_type = record_type
        self.xml = XMLAccessor(xml_element)
        self.all_definitions = get_record_definitions()
        try:
            self.definition = self.all_definitions[record_type]
        except KeyError:
            raise KeyError(
                f"Record definition for '{record_type}' not found in record_definitions.toml"
            )

    def build(self):
        efi_class_name = self.all_definitions["efi_classes"].get(self.record_type)
        if not efi_class_name:
            raise ValueError(
                f"EFI class mapping for record type '{self.record_type}' not found."
            )
        efi_class = getattr(efi, efi_class_name)
        attributes = {}

        if "simple" in self.definition:
            for attr, mapping in self.definition["simple"].items():
                value = self.xml.get_first(mapping["xpath"])
                if value is None:
                    continue
                attributes[attr] = get_mapped_enum_value(mapping["enum"], value)

        if "complex" in self.definition:
            for complex_mapping in self.definition["complex"]:
                attr = complex_mapping["attribute"]
                location = complex_mapping["location"]

                module_path = f"records.{location}.{attr}"

                module = importlib.import_module(module_path)
                func = getattr(module, attr)
                attributes[attr] = func(self.xml)

        return efi_class(**attributes)

from avefi_schema import model_pydantic_v2 as efi

from collections2efi.record import XMLAccessor


def belongs_to(xml: XMLAccessor):
    part_of_list = xml.get_all("Part_of/part_of_reference.lref/text()")
    return [efi.LocalResource(id=priref) for priref in part_of_list]

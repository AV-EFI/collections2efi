from collections2efi.record import XMLAccessor
from collections2efi.record_type.base.belongs_to import belongs_to


def is_part_of(xml: XMLAccessor):
    return belongs_to(xml)

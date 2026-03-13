from avefi_schema import model as efi

from collections2efi.record import XMLAccessor


def has_item(xml: XMLAccessor):
    prirefs = xml.get_all("Parts/parts.reference.lref/text()")

    return [efi.LocalResource(id=priref) for priref in prirefs]

from avefi_schema import model as efi

from records.record import XMLAccessor
from records.utils import get_mapped_enum_value


def has_access_status(xml: XMLAccessor):
    copy_usage = xml.get_first("copy_usage/value[@lang='neutral']/text()")

    if copy_usage == "4":
        return efi.ItemAccessStatusEnum.Removed

    access_status = xml.get_first("copy_status/value[@lang='3']/text()")

    if access_status is None:
        return None

    return get_mapped_enum_value("ItemAccessStatusEnum", access_status)

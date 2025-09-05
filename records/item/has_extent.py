from avefi_schema import model as efi

from records.record import XMLAccessor
from records.utils import get_mapped_enum_value


def has_extent(xml: XMLAccessor):
    dimension_extent = get_dimension_extent(xml)

    if dimension_extent:
        return dimension_extent

    total_filesize_extent = get_total_filesize_extent(xml)

    if total_filesize_extent:
        return total_filesize_extent

    return None


def get_dimension_extent(xml: XMLAccessor):
    unit = xml.get_first(
        "Dimension[dimension.type/value[@lang='de-DE' and text()='Länge']]/dimension.unit/value/text()"
    )
    value = xml.get_first(
        "Dimension[dimension.type/value[@lang='de-DE' and text()='Länge']]/dimension.value/text()"
    )

    if unit is None or value is None:
        return None

    unit_mapped = get_mapped_enum_value("UnitEnum", unit)

    if unit_mapped is None:
        return None

    return efi.Extent(
        has_value=value,
        has_precision=efi.PrecisionEnum.Approximate,
        has_unit=unit_mapped,
    )


def get_total_filesize_extent(xml: XMLAccessor):
    total_filesize = xml.get_first("total_filesize/text()")

    if total_filesize is None:
        return None

    return efi.Extent(
        has_value=total_filesize,
        has_precision=efi.PrecisionEnum.Approximate,
        has_unit=efi.UnitEnum.GigaByte,
    )

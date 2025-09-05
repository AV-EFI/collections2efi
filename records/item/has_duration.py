from avefi_schema import model as efi

from records.record import XMLAccessor
from records.utils import get_mapped_enum_value


def has_duration(xml: XMLAccessor):

    value = xml.get_first(
        "Dimension[dimension.type/value[@lang='de-DE' and text()='Laufzeit']][1]/dimension.value/text()"
    )

    precision = xml.get_first(
        "Dimension[dimension.type/value[@lang='de-DE' and text()='Laufzeit']][1]/dimension.precision/value[@lang='3']/text()"
    )

    if not value:
        return None

    return efi.Duration(
        has_value=time_string_to_iso_8601_duration(value),
        has_precision=(
            get_mapped_enum_value("PrecisionEnum", precision)
            if precision is not None
            else None
        ),
    )


def time_string_to_iso_8601_duration(time_str):

    minute_str, second_str = time_str.split(".") if "." in time_str else (time_str, "0")

    minutes = int(minute_str)
    seconds = int(second_str)

    hours = minutes // 60
    minutes = minutes % 60

    iso_period = "PT"

    if hours > 0:
        iso_period += f"{hours}H"
    if minutes > 0 or seconds > 0:
        iso_period += f"{minutes}M"
    if seconds > 0:
        iso_period += f"{seconds}S"

    return iso_period

from avefi_schema import model as efi

from records.record import XMLAccessor
from records.utils import (
    get_mapped_enum_value,
    get_located_in,
    get_has_date,
)


def has_event(xml: XMLAccessor):
    manifestationlevel_type = xml.get_first(
        "manifestationlevel_type/value[@lang='3']/text()"
    )

    if manifestationlevel_type is None:
        return None

    if manifestationlevel_type == "Fernsehausstrahlung":
        return efi.PublicationEvent(
            type=efi.PublicationEventTypeEnum.BroadcastEvent,
            has_date=xml.get_first("transmission_date/text()"),
        )

    if manifestationlevel_type == "Restauriert":
        return efi.PreservationEvent(
            type=efi.PreservationEventTypeEnum.RestorationEvent,
            has_date=get_has_date(
                xml.get_first("release_date_start/text()"),
                xml.get_first("release_date_end/text()"),
            ),
            located_in=get_located_in(xml.get_all("Production")),
        )

    manifestationlevel_type_mapped = get_mapped_enum_value(
        "PublicationEventTypeEnum", manifestationlevel_type
    )

    if manifestationlevel_type_mapped is None:
        return None

    return efi.PublicationEvent(
        type=manifestationlevel_type_mapped,
        has_date=get_has_date(
            xml.get_first("release_date_start/text()"),
            xml.get_first("release_date_end/text()"),
        ),
    )

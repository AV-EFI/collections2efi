from records.record import XMLAccessor
from records.utils import get_mapped_enum_value


def element_type(xml: XMLAccessor):
    material_type_digital = xml.get_first(
        "material_type_digital/value[@lang='de-DE']/text()"
    )

    material_type_film = xml.get_first(
        "mat_characteristics/mat_characteristics.material_type_film/value[@lang='de-DE']/text()"
    )

    if material_type_digital:
        return get_mapped_enum_value("ItemElementTypeEnum", material_type_digital)

    if material_type_film:
        return get_mapped_enum_value("ItemElementTypeEnum", material_type_film)

    return None

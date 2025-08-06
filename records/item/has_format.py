from avefi_schema import model as efi

from records.record import XMLAccessor
from records.utils import get_mapped_enum_value


def has_format(xml: XMLAccessor):
    return [
        *get_from_file_type(xml),  # DigitalFile
        *get_from_mat_characteristics(xml),  # Audio + Film
        *get_from_material_type_video(xml),  # Video
        *get_from_material_type_digitalvideo(xml),  # Video + Optical
    ]


def get_from_file_type(xml):
    file_type = xml.get_first("file_type/value[@lang='de-DE']/text()")
    if file_type is None:
        return []

    mapped_value = get_mapped_enum_value("FormatDigitalFileTypeEnum", file_type)
    if mapped_value is None:
        return []

    return [efi.DigitalFile(type=mapped_value)]


def get_from_mat_characteristics(xml):
    formats = []

    material_format_film = xml.get_first(
        "mat_characteristics/mat_characteristics.material_format_film/value[@lang='de-DE']/text()"
    )
    material_type_film = xml.get_first(
        "mat_characteristics/mat_characteristics.material_type_film/value[@lang='de-DE']/text()"
    )

    if material_format_film is None:
        return []

    if material_format_film in ["16mm", "17,5mm", "35mm"]:
        if material_type_film == "Magnetband":
            formats.append(
                efi.Audio(
                    type=get_mapped_enum_value(
                        "FormatAudioTypeEnum", material_format_film
                    )
                )
            )
        else:
            formats.append(
                efi.Film(
                    type=get_mapped_enum_value(
                        "FormatFilmTypeEnum", material_format_film
                    )
                )
            )
    else:
        mapped_value_film = get_mapped_enum_value(
            "FormatFilmTypeEnum", material_format_film
        )
        mapped_value_audio = get_mapped_enum_value(
            "FormatAudioTypeEnum", material_format_film
        )

        if mapped_value_film is not None:
            formats.append(efi.Film(type=mapped_value_film))

        if mapped_value_audio is not None:
            formats.append(efi.Audio(type=mapped_value_audio))

    return formats


def get_from_material_type_video(xml):
    material_type_video = xml.get_first(
        "material_type_video/value[@lang='de-DE']/text()"
    )
    if material_type_video is None:
        return []

    mapped_value = get_mapped_enum_value("FormatVideoTypeEnum", material_type_video)
    if mapped_value is None:
        return []

    return [efi.Video(type=mapped_value)]


def get_from_material_type_digitalvideo(xml):
    formats = []
    material_type_digitalvideo = xml.get_first(
        "material_type_digitalvideo/value[@lang='de-DE']/text()"
    )
    if material_type_digitalvideo is None:
        return []

    mapped_value_optical = get_mapped_enum_value(
        "FormatOpticalTypeEnum", material_type_digitalvideo
    )
    mapped_value_video = get_mapped_enum_value(
        "FormatVideoTypeEnum", material_type_digitalvideo
    )

    if mapped_value_optical is not None:
        formats.append(efi.Optical(type=mapped_value_optical))

    if mapped_value_video is not None:
        formats.append(efi.Video(type=mapped_value_video))

    return formats

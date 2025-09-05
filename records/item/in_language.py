from avefi_schema import model as efi

from records.record import XMLAccessor
from records.utils import get_mapped_enum_value


def in_language(xml: XMLAccessor):

    xml_languages_list = xml.get_all("Language")

    languages = []

    for xml_language in xml_languages_list:

        language = xml_language.get_first("language/value[@lang='de-DE']/text()")
        language_type = xml_language.get_first("language.type/value[@lang='3']/text()")
        if language is None or language_type is None:
            continue

        language_mapped = get_mapped_enum_value("LanguageCodeEnum", language)
        language_type_mapped = get_mapped_enum_value("LanguageUsageEnum", language_type)

        if language_mapped is None or language_type_mapped is None:
            continue

        languages.append(
            efi.Language(
                code=language_mapped,
                usage=language_type_mapped,
            )
        )

    return languages

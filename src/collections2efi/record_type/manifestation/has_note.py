from avefi_schema import model_pydantic_v2 as efi

from collections2efi.record import XMLAccessor


def has_note(xml: XMLAccessor):
    notes = xml.get_all(
        "Content_description/content.description/value[@lang='de-DE']/text()"
    )

    return notes

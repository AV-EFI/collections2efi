from dataclasses import dataclass

from avefi_schema import model as efi

from collections2efi.record import XMLAccessor
from collections2efi.record_type.base.utils import (
    compute_display_and_ordering_title,
    get_mapped_enum_value,
)


@dataclass()
class TempTitle:
    name: str
    type: str
    ordering_name: str


def compute_title(xml: XMLAccessor):
    xml_titles = xml.get_all("Title")

    temp_titles: list[TempTitle] = []

    for xml_title in xml_titles:
        title_text = xml_title.get_first("title/text()")
        title_type = xml_title.get_first("title.type/value[@lang='de-DE']/text()")
        title_article = xml_title.get_first("title.article/text()")

        new_title_text, ordering_title_text = compute_display_and_ordering_title(
            title_text, title_article
        )

        temp_titles.append(
            TempTitle(
                name=new_title_text, type=title_type, ordering_name=ordering_title_text
            )
        )

    if len(temp_titles) == 0:
        raise Exception("No title found")

    primary_title = efi.Title(
        has_name=temp_titles[0].name,
        type=(
            efi.TitleTypeEnum.SuppliedDevisedTitle
            if temp_titles[0].type == "Archivtitel"
            else efi.TitleTypeEnum.PreferredTitle
        ),
        has_ordering_name=temp_titles[0].ordering_name,
    )

    titles = [primary_title]

    # all other titles

    for temp_title in temp_titles[1:]:
        title_type_mapped = get_mapped_enum_value("TitleTypeEnum", temp_title.type)

        titles.append(
            efi.Title(
                has_name=temp_title.name,
                type=(
                    title_type_mapped
                    if title_type_mapped
                    else efi.TitleTypeEnum.AlternativeTitle
                ),
                has_ordering_name=temp_title.ordering_name,
            )
        )

    return titles

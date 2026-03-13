from avefi_schema import model_pydantic_v2 as efi

from collections2efi.record import XMLAccessor
from collections2efi.record_type.base.utils import compute_display_and_ordering_title


def has_primary_title(xml: XMLAccessor):
    # first check own title

    own_title_text = xml.get_first("Title/title/text()")
    own_title_article = xml.get_first("Title/title.article/text()")
    own_title_type = xml.get_first("Title/title.type/value[@lang='de-DE']/text()")

    if own_title_text is not None:
        new_title_text, ordering_title_text = compute_display_and_ordering_title(
            own_title_text, own_title_article
        )
        return efi.Title(
            type=(
                efi.TitleTypeEnum.SuppliedDevisedTitle
                if own_title_type == "Archivtitel"
                else efi.TitleTypeEnum.TitleProper
            ),
            has_name=new_title_text,
            has_ordering_name=ordering_title_text,
        )

    # then check top level work

    top_level_work_title_text = xml.get_first(
        "Part_of/part_of_reference/Part_of/part_of.title/text()"
    )
    top_level_work_lead_word = xml.get_first(
        "Part_of/part_of_reference/Part_of/part_of.lead_word/text()"
    )
    if top_level_work_title_text is not None:
        new_title_text, ordering_title_text = compute_display_and_ordering_title(
            top_level_work_title_text, top_level_work_lead_word
        )
        return efi.Title(
            type=efi.TitleTypeEnum.TitleProper,
            has_name=new_title_text,
            has_ordering_name=ordering_title_text,
        )

    # lastly, check work

    work_title_text = xml.get_first("Part_of/part_of.title/text()")
    work_lead_word = xml.get_first("Part_of/part_of.lead_word/text()")

    assert work_title_text is not None

    new_title_text, ordering_title_text = compute_display_and_ordering_title(
        work_title_text, work_lead_word
    )
    return efi.Title(
        type=efi.TitleTypeEnum.TitleProper,
        has_name=new_title_text,
        has_ordering_name=ordering_title_text,
    )

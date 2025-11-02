from avefi_schema import model as efi

from collections2efi.record import XMLAccessor


def has_primary_title(xml: XMLAccessor):
    title = xml.get_first("Title/title/text()")

    title_article = xml.get_first("Title/title.article/text()")

    if title is not None:
        title = title if not title_article else title_article + " " + title
    else:
        part_of_title = xml.get_first("Part_of/part_of.title/text()")
        part_of_lead_word = xml.get_first("Part_of/part_of.lead_word/text()")
        if part_of_lead_word is not None:
            title = part_of_lead_word + " " + part_of_title
        else:
            title = part_of_title

    return efi.Title(type=efi.TitleTypeEnum.PreferredTitle, has_name=title)

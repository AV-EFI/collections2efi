from avefi_schema import model as efi

from mappings.title_type_enum_mapping import title_type_enum_mapping
from records.base.base_record import BaseRecord
from records.base.utils import get_mapped_enum_value


def compute_has_alternative_title(record: BaseRecord):
    return compute_title(record)[1:]


def compute_has_primary_title(record: BaseRecord):
    return compute_title(record)[0]


def compute_title(record: BaseRecord):

    xml_titles = record.xml.get_all("Title")
    titles = []

    for xml_title in xml_titles:

        title_text = xml_title.get_first("title/text()")
        title_type = xml_title.get_first("title.type/value[@lang='de-DE']/text()")
        title_article = xml_title.get_first("title.article/text()")

        if title_text is None:
            continue

        ordering_title_text = None
        new_title_text = title_text

        if title_article is not None:
            new_title_text = f"{title_article} {title_text}"
            ordering_title_text = f"{title_text}, {title_article}"

        new_title_type = efi.TitleTypeEnum.AlternativeTitle

        if title_type is not None:
            title_type_mapped = get_mapped_enum_value(
                title_type_enum_mapping, title_type
            )
            if title_type_mapped is not None:
                new_title_type = title_type_mapped

        titles.append(
            efi.Title(
                has_name=new_title_text,
                type=new_title_type,
                has_ordering_name=ordering_title_text,
            )
        )

    def title_sort(title):
        if str(title.type) == str(efi.TitleTypeEnum.PreferredTitle.text):
            return 0
        if str(title.type) == str(efi.TitleTypeEnum.SuppliedDevisedTitle.text):
            return 1
        return 2

    titles.sort(key=lambda x: title_sort(x))

    return titles

import logging
import re
import datetime

from avefi_schema import model_pydantic_v2 as efi

from collections2efi.mappings.loader import get_mapping
from collections2efi.record import PeopleRecord, ThesauRecord


def get_has_date(
    date_start,
    date_end,
    date_start_prec=None,
    date_end_prec=None,
):
    start = f"{date_start}{'~' if date_start_prec else ''}" if date_start else None
    end = f"{date_end}{'~' if date_end_prec else ''}" if date_end else None

    if start and end:
        return start if start == end else f"{start}/{end}"
    return start or end


def get_same_as_for_record(
    record: ThesauRecord | PeopleRecord,
    include_gnd: bool = False,
    include_filmportal: bool = False,
    include_tgn: bool = False,
):

    same_as = []

    xml_sources = record.xml.xpath("Source")

    for source_xml in xml_sources:
        source_number = source_xml.xpath("string(source.number[1])") or None

        if source_number is None:
            continue

        if include_gnd and "d-nb.info/gnd/" in source_number:
            same_as.append(
                efi.GNDResource(
                    id=source_number.split("/")[-1],
                )
            )

        if include_filmportal and "www.filmportal.de" in source_number:
            # temporary solution
            filmportal_id = source_number.split("_")[-1]
            if not re.fullmatch(r"^[\da-f]{32}$", filmportal_id):
                continue

            same_as.append(
                efi.FilmportalResource(
                    id=filmportal_id,
                )
            )

        if include_tgn and "vocab.getty.edu/page/tgn/" in source_number:
            same_as.append(
                efi.TGNResource(
                    id=source_number.split("/")[-1],
                )
            )
    return same_as


def get_mapped_enum_value(enum_name, key):
    enum = get_mapping(enum_name)

    if key not in enum:
        logging.warning(f"No mapping found for key: '{key}' in {enum_name}")
        return None

    return enum[key]


def get_located_in(xml_productions, thesau_repo):
    located_in = []

    for xml_production in xml_productions:
        production_country = xml_production.get_first(
            "production_country/value[@lang='de-DE']/text()"
        )
        priref = xml_production.get_first("production_country.lref/text()")

        if production_country is None or priref is None:
            continue

        located_in.append(
            efi.GeographicName(
                has_name=production_country,
                same_as=get_same_as_for_record(
                    thesau_repo.get_record(priref),
                    include_gnd=True,
                    include_tgn=True,
                ),
            )
        )

    return located_in


def compute_display_and_ordering_title(
    title_text: str, title_article: str | None
) -> tuple[str, str | None]:
    new_title_text = title_text

    if title_article is None:
        return new_title_text, None

    return f"{title_article} {title_text}", f"{title_text}, {title_article}"

def get_description_resource():
    return efi.DescriptionResource(
        has_issuer_id="https://w3id.org/isil/DE-MUS-407010",
        has_issuer_name="Deutsche Kinemathek - Museum für Film und Fernsehen",
        last_modified=datetime.datetime.now(datetime.timezone.utc),
    )
import logging
import re

from avefi_schema import model as efi

from axiell_collections import thesau_provider
from mappings.loader import get_mapping


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


def get_same_as_for_priref(
    priref,
    provider,
    include_gnd=False,
    include_filmportal=False,
    include_tgn=False,
):

    try:
        same_as = []

        xml_data = provider.get_by_priref(priref)
        xml_sources = xml_data.xpath("Source")

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

    except Exception as e:
        raise Exception("Problem with same_as computation:", e)


def get_mapped_enum_value(enum_name, key):
    enum = get_mapping(enum_name)

    if key not in enum:
        logging.warning(f"No mapping found for key: '{key}' in {enum_name}")
        return None

    return enum[key]


def get_located_in(xml_productions):
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
                same_as=get_same_as_for_priref(
                    priref,
                    thesau_provider,
                    include_gnd=True,
                    include_tgn=True,
                ),
            )
        )

    return located_in

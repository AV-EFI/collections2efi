from avefi_schema import model as efi

from axiell_collections import thesau_provider
from records.record import XMLAccessor
from records.utils import get_same_as_for_priref


def has_genre(xml: XMLAccessor):
    xml_content_genres = xml.get_all("Content_genre")

    genres = []

    for xml_content_genre in xml_content_genres:
        genre_name = xml_content_genre.get_first("content.genre/value/text()")
        priref = xml_content_genre.get_first("content.genre.lref/text()")

        if genre_name is None or priref is None:
            continue

        genre = efi.Genre(
            has_name=genre_name,
            same_as=get_same_as_for_priref(
                priref,
                thesau_provider,
                include_gnd=True,
            ),
        )
        genres.append(genre)

    return genres

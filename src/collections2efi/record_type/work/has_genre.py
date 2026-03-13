from avefi_schema import model_pydantic_v2 as efi

from collections2efi.record import XMLAccessor
from collections2efi.record_type.base.utils import get_same_as_for_record
from collections2efi.repositories import ThesauRepo


def has_genre(xml: XMLAccessor, thesau_repo: ThesauRepo):
    xml_content_genres = xml.get_all("Content_genre")

    genres = []

    for xml_content_genre in xml_content_genres:
        genre_name = xml_content_genre.get_first("content.genre/value/text()")
        priref = xml_content_genre.get_first("content.genre.lref/text()")

        if genre_name is None or priref is None:
            continue

        genre = efi.Genre(
            has_name=genre_name,
            same_as=get_same_as_for_record(
                thesau_repo.get_record(priref),
                include_gnd=True,
            ),
        )
        genres.append(genre)

    return genres

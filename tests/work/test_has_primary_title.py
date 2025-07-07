from avefi_schema import model as efi
from requests import Session

from axiell_collections import collect_provider, axiell_collections_database
from records.record import XMLAccessor
from records.work.has_primary_title import has_primary_title


def test_has_primary_title(monkeypatch):
    monkeypatch.setattr(axiell_collections_database, "session", Session())

    raw_xml = collect_provider.get_by_priref("200000127")
    xml = XMLAccessor(raw_xml)

    assert has_primary_title(xml) == efi.Title(
        has_name="La Amiga",
        type=efi.TitleTypeEnum.PreferredTitle,
        has_ordering_name="Amiga, La",
    )

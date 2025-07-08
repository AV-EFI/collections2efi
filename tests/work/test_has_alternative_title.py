import pytest
from avefi_schema import model as efi

from records.work.has_alternative_title import has_alternative_title


@pytest.mark.parametrize(
    "priref, expected",
    [
        (
            "200000127",
            [
                efi.Title(
                    has_name="La Amiga - Die Freundin",
                    type=efi.TitleTypeEnum.PreferredTitle,
                    has_ordering_name="Amiga - Die Freundin, La",
                )
            ],
        )
    ],
)
def test_has_alternative_title(all_records, priref, expected):
    xml = all_records[priref]
    assert has_alternative_title(xml) == expected

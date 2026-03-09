import pytest
from avefi_schema import model as efi

from records.manifestation.has_primary_title import has_primary_title


@pytest.mark.parametrize(
    "priref, expected",
    [
        (
            "200339241",  # Manifestion without a title and no top level work, so work title chosen
            efi.Title(
                has_name="Picasso in Vallauris - Kurzfassung",
                type=efi.TitleTypeEnum.TitleProper,
            ),
        ),
    ],
)
def test_has_primary_title(all_records, priref, expected):
    xml = all_records[priref]
    assert has_primary_title(xml) == expected

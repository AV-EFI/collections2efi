import pytest
from avefi_schema import model as efi

from collections2efi.record_type.item.has_primary_title import has_primary_title


@pytest.mark.parametrize(
    "priref, expected",
    [
        (
            "200322201",
            efi.Title(
                has_name="Die Geschichten vom Kübelkind",
                has_ordering_name="Geschichten vom Kübelkind, Die",
                type=efi.TitleTypeEnum.TitleProper,
            ),
        ),
    ],
)
def test_has_primary_title(all_records, priref, expected):
    xml = all_records[priref]
    assert has_primary_title(xml) == expected

import pytest
from avefi_schema import model as efi

from collections2efi.record_type.work.has_primary_title import has_primary_title


@pytest.mark.parametrize(
    "priref, expected",
    [
        (
            "200000127",
            efi.Title(
                has_name="La Amiga",
                type=efi.TitleTypeEnum.PreferredTitle,
                has_ordering_name="Amiga, La",
            ),
        )
    ],
)
def test_has_primary_title(collect_record_factory, priref, expected):
    xml = collect_record_factory(priref).xml
    assert has_primary_title(xml) == expected

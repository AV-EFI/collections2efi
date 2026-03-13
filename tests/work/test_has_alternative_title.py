import pytest
from avefi_schema import model_pydantic_v2 as efi

from collections2efi.record_type.work.has_alternative_title import has_alternative_title


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
def test_has_alternative_title(collect_record_factory, priref, expected):
    xml = collect_record_factory(priref).xml
    assert has_alternative_title(xml) == expected

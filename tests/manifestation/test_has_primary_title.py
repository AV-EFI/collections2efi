import pytest
from avefi_schema import model_pydantic_v2 as efi

from collections2efi.record_type.manifestation.has_primary_title import (
    has_primary_title,
)


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
def test_has_primary_title(collect_record_factory, priref, expected):
    xml = collect_record_factory(priref).xml
    assert has_primary_title(xml) == expected

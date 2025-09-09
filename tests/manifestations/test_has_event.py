import pytest
from avefi_schema import model as efi

from records.manifestation.has_event import has_event


@pytest.mark.parametrize(
    "priref, expected",
    [
        (
            "200323440",
            [
                efi.PublicationEvent(
                    type=efi.PublicationEventTypeEnum.BroadcastEvent,
                    has_date="1989-08-15",
                ),
            ],
        ),
        (
            "200152050",
            [
                efi.PreservationEvent(
                    type=efi.PreservationEventTypeEnum.RestorationEvent,
                    has_date="2010",
                    located_in=[
                        efi.GeographicName(
                            has_name="Deutschland",
                            same_as=[
                                efi.GNDResource(id="4011882-4"),
                                efi.TGNResource(id="7000084"),
                            ],
                        )
                    ],
                )
            ],
        ),
        (
            "200044362",
            [
                efi.PublicationEvent(
                    type=efi.PublicationEventTypeEnum.TheatricalDistributionEvent,
                    has_date="1985",
                )
            ],
        ),
    ],
)
def test_has_event(all_records, priref, expected):
    xml = all_records[priref]
    assert has_event(xml) == expected

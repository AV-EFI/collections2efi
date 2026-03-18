import pytest

from collections2efi.repositories import PeopleRepo, ThesauRepo
from collections2efi.translator import Translator


@pytest.mark.parametrize("priref", ["200000687", "200236329", "200221452", "200322007"])
def test_complete_record(
    collect_record_factory,
    thesau_repo: ThesauRepo,
    people_repo: PeopleRepo,
    priref,
    data_regression,
):

    record = collect_record_factory(priref)
    translator = Translator(
        people_repo=people_repo,
        thesau_repo=thesau_repo,
    )

    actual_data = translator.translate(record).model_dump(
        mode="json", exclude_none=True
    )

    # Sanitize time-specific filed last_updated, see different handling for different logic
    record_type = record.xml.get_first(
        "record_type/value[@lang='neutral']/text()"
    ).lower()
    if record_type in ["item", "manifestation"]:
        actual_data["described_by"]["last_modified"] = "2024-01-01T00:00:00"

    elif record_type == "work":
        actual_data["described_by"][0]["last_modified"] = "2024-01-01T00:00:00"

    data_regression.check(actual_data)

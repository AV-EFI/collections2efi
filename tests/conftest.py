import os

import pytest

from axiell_collections import RecordProvider, Database
from records.record import XMLAccessor

RECORD_PRIREFS = ["200000127", "200000151"]


@pytest.fixture(scope="session")
def all_records():
    axiell_collections_url = os.environ["SDK_AXIELL_COLLECTIONS_URL"]
    collect_provider = RecordProvider(
        Database(axiell_collections_url), database="collect.inf"
    )

    return {
        priref: XMLAccessor(collect_provider.get_by_priref(priref))
        for priref in RECORD_PRIREFS
    }

from pathlib import Path

import pytest
from lxml import etree

from collections2efi.record import CollectRecord, PeopleRecord, ThesauRecord
from collections2efi.repositories import PeopleRepo, ThesauRepo


@pytest.fixture
def records_path() -> Path:
    return Path(__file__).parent / "test_records"


@pytest.fixture
def collect_record_factory(records_path):
    def _factory(priref: str) -> CollectRecord:
        file_path = records_path / "collect" / f"{priref}.xml"
        with open(file_path, "rb") as f:
            xml_element = etree.fromstring(f.read())
        return CollectRecord(xml_element)

    return _factory


@pytest.fixture
def people_repo(records_path) -> PeopleRepo:
    repo = PeopleRepo()
    people_dir = records_path / "people"
    for file_path in people_dir.glob("*.xml"):
        with open(file_path, "rb") as f:
            xml_element = etree.fromstring(f.read())
        record = PeopleRecord(xml_element)
        repo.add_records({record.priref: record})
    return repo


@pytest.fixture
def thesau_repo(records_path) -> ThesauRepo:
    repo = ThesauRepo()
    thesau_dir = records_path / "thesau"
    for file_path in thesau_dir.glob("*.xml"):
        with open(file_path, "rb") as f:
            xml_element = etree.fromstring(f.read())
        record = ThesauRecord(xml_element)
        repo.add_records({record.priref: record})
    return repo

from typing import Generic, TypeVar

from collections2efi.record import PeopleRecord, Record, ThesauRecord

T = TypeVar("T", bound=Record)


class Repository(Generic[T]):
    def __init__(self):
        self._data: dict[str, T] = {}

    def __len__(self):
        return len(self._data)

    def add_records(self, records: dict[str, T]):
        self._data.update(records)

    def get_record(self, priref: str) -> T:
        record = self._data.get(priref)
        assert record is not None
        return record


class PeopleRepo(Repository[PeopleRecord]):
    def __init__(self):
        super().__init__()


class ThesauRepo(Repository[ThesauRecord]):
    def __init__(self):
        super().__init__()

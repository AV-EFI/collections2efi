class Repository:
    def __init__(self):
        self._data = {}

    def add_records(self, records: dict):
        self._data.update(records)

    def get_record(self, priref: str):
        record = self._data.get(priref)
        if record is None:
            print("No record found for priref '{}'".format(priref))
        return record


class PeopleRepo(Repository):
    def __init__(self):
        super().__init__()


class ThesauRepo(Repository):
    def __init__(self):
        super().__init__()

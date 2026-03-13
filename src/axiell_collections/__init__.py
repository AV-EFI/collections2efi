import os

from requests_cache import CachedSession

from axiell_collections.provider import RecordProvider, PointerFileProvider
from axiell_collections.wrapper import Database


class CachedDatabase(Database):
    def __init__(self, url):
        super().__init__(url)
        self.session = CachedSession(cache_name="axiell_collections_cache")


try:
    axiell_collections_url = os.environ["SDK_AXIELL_COLLECTIONS_URL"]
    axiell_collections_database = CachedDatabase(axiell_collections_url)
except KeyError:
    raise EnvironmentError(
        "SDK_AXIELL_COLLECTIONS_URL environment variable is not set."
    )

pointer_file_provider = PointerFileProvider(
    axiell_collections_database, database="collect.inf"
)
collect_provider = RecordProvider(axiell_collections_database, database="collect.inf")
people_provider = RecordProvider(axiell_collections_database, database="people.inf")
thesau_provider = RecordProvider(axiell_collections_database, database="thesau.inf")

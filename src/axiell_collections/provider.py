from abc import ABC, abstractmethod


class BaseProvider(ABC):
    def __init__(self, axiell_collections, database):
        self.axiell_collections = axiell_collections
        self.database = database

    def get_by_priref(self, priref):
        query = self._construct_query(priref)
        data_xml = self._execute_query(query)

        return data_xml

    def _execute_query(self, query):
        result = self.axiell_collections.get(query)
        try:
            return result.records[0]
        except IndexError:
            raise IndexError("Did not receive a record")
        except Exception as e:
            raise Exception(f"An error occurred during the request: {e}")

    @abstractmethod
    def _construct_query(self, priref):
        pass


class RecordProvider(BaseProvider):
    def _construct_query(self, priref):
        return {
            "search": f"priref={priref}",
            "database": self.database,
            "xmltype": "grouped",
        }


class PointerFileProvider(BaseProvider):
    def _construct_query(self, priref):
        return {
            "database": self.database,
            "xmltype": "grouped",
            "command": "getpointerfile",
            "number": priref,
        }

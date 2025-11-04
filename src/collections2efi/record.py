from abc import ABC


class XMLAccessor:
    def __init__(self, xml_element):
        self._element = xml_element

    def get_first(self, xpath_expression):
        elements = self._element.xpath(xpath_expression)

        return elements[0] if elements else None

    def get_all(self, xpath_expression):
        elements = self._element.xpath(xpath_expression)

        if xpath_expression.endswith("/text()"):
            return elements

        return [XMLAccessor(el) for el in elements]

    def __getattr__(self, name):
        return getattr(self._element, name)

    def __repr__(self):
        return f"<XMLAccessor wrapping {self._element!r}>"


class Record(ABC):
    def __init__(self, xml_element):
        self.xml = XMLAccessor(xml_element)
        self.priref = self.xml.get_first("@priref")


class ThesauRecord(Record):
    def __init__(self, xml_element):
        super().__init__(xml_element)


class PeopleRecord(Record):
    def __init__(self, xml_element):
        super().__init__(xml_element)


class CollectRecord(Record):
    def __init__(self, xml_element):
        super().__init__(xml_element)

    def _get_connected_prirefs(self, xpaths: tuple) -> set[str]:
        return set(priref for xpath in xpaths for priref in self.xml.get_all(xpath))

    def get_connected_thesau_prirefs(self) -> set[str]:
        xpaths = (
            "Production/production_country.lref/text()",
            "Content_genre/content.genre.lref/text()",
            "Content_subject/content.subject.lref/text()",
            "ContentGeo/content.geographical_keyword.lref/text()",
        )
        return self._get_connected_prirefs(xpaths)

    def get_connected_people_prirefs(self) -> set[str]:
        xpaths = (
            "Cast/cast.name.lref/text()",
            "Credits/credit.name.lref/text()",
            "Content_person/content.person.name.lref/text()",
        )
        return self._get_connected_prirefs(xpaths)

    def get_connected_collect_prirefs(self) -> set[str]:
        xpaths = (
            "Part_of/part_of_reference.lref/text()",
            "Parts/parts.reference.lref/text()",
        )
        return self._get_connected_prirefs(xpaths)

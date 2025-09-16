from avefi_schema import model as efi

from axiell_collections import thesau_provider, people_provider
from records.record import XMLAccessor
from records.utils import get_same_as_for_priref


def has_subject(xml: XMLAccessor):
    return (
        get_from_content_person(xml)
        + get_from_content_subject(xml)
        + get_from_geographical_keyword(xml)
    )


def get_from_content_subject(xml):
    subjects = []
    for xml_content_subject in xml.get_all("Content_subject"):

        subject_name = xml_content_subject.get_first(
            "content.subject/value[@lang='de-DE']/text()"
        )
        priref = xml_content_subject.get_first("content.subject.lref/text()")

        if subject_name is None or priref is None:
            continue

        same_as = get_same_as_for_priref(
            priref,
            thesau_provider,
            include_gnd=True,
            include_filmportal=True,
            include_tgn=True,
        )

        subject_type = (
            efi.GeographicName
            if "avefi:TGNResource" in [identifier.category for identifier in same_as]
            else efi.Subject
        )

        subjects.append(
            subject_type(
                has_name=subject_name,
                same_as=same_as,
            )
        )

    return subjects


def get_from_geographical_keyword(xml):

    geographic_names = []

    for xml_geographical_keyword in xml.get_all("ContentGeo"):

        geographical_keyword_name = xml_geographical_keyword.get_first(
            "content.geographical_keyword/value[@lang='de-DE']/text()"
        )
        priref = xml_geographical_keyword.get_first(
            "content.geographical_keyword.lref/text()"
        )

        if geographical_keyword_name is None or priref is None:
            continue

        geographic_names.append(
            efi.GeographicName(
                has_name=geographical_keyword_name,
                same_as=get_same_as_for_priref(
                    priref,
                    thesau_provider,
                    include_gnd=True,
                    include_filmportal=True,
                    include_tgn=True,
                ),
            )
        )

    return geographic_names


def get_from_content_person(xml):
    persons = []

    for xml_content_person in xml.get_all("Content_person"):

        person_name = xml_content_person.get_first("content.person.name/value/text()")
        priref = xml_content_person.get_first("content.person.name.lref/text()")

        if person_name is None or priref is None:
            continue

        person = efi.Agent(
            has_name=person_name,
            same_as=get_same_as_for_priref(
                priref,
                people_provider,
                include_gnd=True,
                include_filmportal=True,
            ),
            type=(
                efi.AgentTypeEnum.CorporateBody
                if XMLAccessor(people_provider.get_by_priref(priref)).get_first(
                    "record_type/value[@lang='neutral']/text()"
                )
                == "2"
                else efi.AgentTypeEnum.Person
            ),
        )
        persons.append(person)

    return persons

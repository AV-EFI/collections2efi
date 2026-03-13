from avefi_schema import model as efi

from collections2efi.record import XMLAccessor
from collections2efi.record_type.base.utils import get_same_as_for_record
from collections2efi.repositories import PeopleRepo, ThesauRepo


def has_subject(
    xml: XMLAccessor,
    people_repo: PeopleRepo,
    thesau_repo: ThesauRepo,
):
    return (
        get_from_content_person(xml, people_repo)
        + get_from_content_subject(xml, thesau_repo)
        + get_from_geographical_keyword(xml, thesau_repo)
    )


def get_from_content_subject(xml: XMLAccessor, thesau_repo: ThesauRepo):
    subjects = []
    for xml_content_subject in xml.get_all("Content_subject"):
        subject_name = xml_content_subject.get_first(
            "content.subject/value[@lang='de-DE']/text()"
        )
        priref = xml_content_subject.get_first("content.subject.lref/text()")

        if subject_name is None or priref is None:
            continue

        same_as = get_same_as_for_record(
            thesau_repo.get_record(priref),
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


def get_from_geographical_keyword(xml: XMLAccessor, thesau_repo: ThesauRepo):

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
                same_as=get_same_as_for_record(
                    thesau_repo.get_record(priref),
                    include_gnd=True,
                    include_filmportal=True,
                    include_tgn=True,
                ),
            )
        )

    return geographic_names


def get_from_content_person(xml: XMLAccessor, people_repo: PeopleRepo):
    persons = []

    for xml_content_person in xml.get_all("Content_person"):
        person_name = xml_content_person.get_first("content.person.name/value/text()")
        priref = xml_content_person.get_first("content.person.name.lref/text()")

        if person_name is None or priref is None:
            continue

        people_record = people_repo.get_record(priref)

        person = efi.Agent(
            has_name=person_name,
            same_as=get_same_as_for_record(
                people_record,
                include_gnd=True,
                include_filmportal=True,
            ),
            type=(
                efi.AgentTypeEnum.CorporateBody
                if people_record.xml.get_first(
                    "record_type/value[@lang='neutral']/text()"
                )
                == "2"
                else efi.AgentTypeEnum.Person
            ),
        )
        persons.append(person)

    return persons

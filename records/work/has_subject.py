from avefi_schema import model as efi

from axiell_collections import thesau_provider, people_provider
from records.record import XMLAccessor
from records.utils import get_same_as_for_priref


def has_subject(xml: XMLAccessor):
    # Agent (Person) handling
    xml_content_persons = xml.get_all("Content_person")

    persons = []

    for xml_content_person in xml_content_persons:

        person_name = xml_content_person.get_first("content.person.name/value/text()")
        priref = xml_content_person.get_first("content.person.name.lref/text()")

        if person_name is None or priref is None:
            continue

        # CURRENTLY WRONG !!!! HOW TO DECIDE WHICH AGENT TYPE ????

        person = efi.Agent(
            has_name=person_name,
            same_as=get_same_as_for_priref(
                priref,
                people_provider,
                include_gnd=True,
                include_filmportal=True,
                include_tgn=True,
            ),
            type=efi.AgentTypeEnum.Person,
        )
        persons.append(person)

    # Subject and GeographicName handling

    xml_content_subjects = xml.get_all("Content_subject")

    subjects = []
    geographic_names = []

    for xml_content_subject in xml_content_subjects:

        subject_name = xml_content_subject.get_first(
            "content.subject/value[@lang='de-DE']/text()"
        )
        priref = xml_content_subject.get_first("content.subject.lref/text()")

        if subject_name is None or priref is None:
            continue

        subject_xml = thesau_provider.get_by_priref(priref)

        same_as = get_same_as_for_priref(
            priref,
            thesau_provider,
            include_gnd=True,
            include_filmportal=True,
            include_tgn=True,
        )

        term_types = subject_xml.xpath("term.type/value[@lang='3']/text()")

        if "Ort" in term_types:
            geographic_names.append(
                efi.GeographicName(
                    has_name=subject_name,
                    same_as=same_as,
                )
            )

        if "Ort" not in term_types:
            subjects.append(
                efi.Subject(
                    has_name=subject_name,
                    same_as=same_as,
                )
            )

    return persons + subjects + geographic_names

import logging
import logging.config
import logging.handlers
import os
import pathlib
import tempfile
import time
import tomllib
from datetime import datetime

from linkml_runtime.dumpers import JSONDumper

from axiell_collections import (
    collect_provider,
    pointer_file_provider,
    people_provider,
    thesau_provider,
)
from collections2efi import Record, Translator, PeopleRepo, ThesauRepo

logger = logging.getLogger("collections2efi")


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    config_file = pathlib.Path("logging_config.toml")
    with open(config_file, "rb") as f_in:
        config_file = tomllib.load(f_in)
    logging.config.dictConfig(config_file)


setup_logging()


def main():

    start = time.time()

    work_prirefs = pointer_file_provider.get_by_priref(3).xpath("hit/text()")
    manifestation_prirefs = pointer_file_provider.get_by_priref(4).xpath("hit/text()")
    item_prirefs = pointer_file_provider.get_by_priref(5).xpath("hit/text()")

    prirefs = work_prirefs + manifestation_prirefs + item_prirefs

    logging.info(f"# Retrieved {len(prirefs)} prirefs")

    records = get_records(prirefs)

    people_prirefs = set()
    thesau_prirefs = set()

    for record in records:
        for xpath in [
            "Cast/cast.name.lref/text()",
            "Credits/credit.name.lref/text()",
            "Content_person/content.person.name.lref/text()",
        ]:
            people_prirefs.update(record.xml.get_all(xpath))
        for xpath in [
            "Production/production_country.lref/text()",
            "Content_genre/content.genre.lref/text()",
            "Content_subject/content.subject.lref/text()",
            "ContentGeo/content.geographical_keyword.lref/text()",
        ]:
            thesau_prirefs.update(record.xml.get_all(xpath))

    people_repo = PeopleRepo()
    thesau_repo = ThesauRepo()

    people_repo.add_records(
        {
            priref: Record(people_provider.get_by_priref(priref))
            for priref in people_prirefs
        },
    )
    thesau_repo.add_records(
        {
            priref: Record(thesau_provider.get_by_priref(priref))
            for priref in thesau_prirefs
        },
    )

    efi_records = build_records(
        records,
        people_repo=people_repo,
        thesau_repo=thesau_repo,
    )

    logging.info(f"# Built {len(efi_records)} records")

    purged_records = purge_records(efi_records)

    logging.info(f"# After purge: {len(purged_records)} records")

    file_obj, json_file = tempfile.mkstemp(
        prefix=datetime.now().strftime("%Y%m%d-%H%M%S-"),
        suffix=".json",
    )
    os.close(file_obj)

    dumper = JSONDumper()
    dumper.dump(purged_records, json_file, inject_type=False)

    print(f"Wrote data to file://{json_file}")
    end = time.time()
    print(end - start)


def get_records(prirefs) -> list[Record]:
    records = []
    for priref in prirefs:
        record = Record(collect_provider.get_by_priref(priref))
        records.append(record)
    return records


def build_records(
    records: list[Record],
    people_repo: PeopleRepo,
    thesau_repo: ThesauRepo,
):
    built_records = []
    translator = Translator(
        people_repo=people_repo,
        thesau_repo=thesau_repo,
    )
    for record in records:
        logging.info(f"Handling record with priref {record.xml.get_first('@priref')}")
        try:
            built_record = translator.translate(record)
            built_records.append(built_record)
        except Exception as e:
            logging.error(
                f"Error during mapping of {record.xml.get_first('@priref')}: {e}",
                exc_info=True,
            )
            pass
    return built_records


def purge_records(records):
    works = list(filter(lambda r: r.category == "avefi:WorkVariant", records))
    manifestations = list(
        filter(lambda r: r.category == "avefi:Manifestation", records)
    )
    items = list(filter(lambda r: r.category == "avefi:Item", records))

    work_prirefs = {work.has_identifier[0].id for work in works}
    purged_works = [
        work
        for work in works
        if all(parent.id in work_prirefs for parent in work.is_part_of)
    ]

    purged_work_prirefs = {work.has_identifier[0].id for work in purged_works}
    purged_manifestations = [
        manifestation
        for manifestation in manifestations
        if all(
            parent.id in purged_work_prirefs
            for parent in manifestation.is_manifestation_of
        )
    ]

    purged_manifestation_prirefs = {
        manifestation.has_identifier[0].id for manifestation in purged_manifestations
    }
    purged_items = [
        item
        for item in items
        if item.is_item_of and item.is_item_of.id in purged_manifestation_prirefs
    ]

    return purged_works + purged_manifestations + purged_items


if __name__ == "__main__":
    main()

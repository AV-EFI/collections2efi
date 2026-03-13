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
    people_provider,
    pointer_file_provider,
    thesau_provider,
)
from collections2efi.record import (
    CollectRecord,
    PeopleRecord,
    ThesauRecord,
)
from collections2efi.repositories import (
    PeopleRepo,
    ThesauRepo,
)
from collections2efi.translator import (
    Translator,
)

logger = logging.getLogger("collections2efi")


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    config_file = pathlib.Path("logging_config.toml")
    with open(config_file, "rb") as f_in:
        config_file = tomllib.load(f_in)
    logging.config.dictConfig(config_file)


setup_logging()


def get_prirefs_from_pointer_files() -> list[str]:
    work_prirefs = pointer_file_provider.get_by_priref(3).xpath("hit/text()")
    manifestation_prirefs = pointer_file_provider.get_by_priref(4).xpath("hit/text()")
    item_prirefs = pointer_file_provider.get_by_priref(5).xpath("hit/text()")
    return work_prirefs + manifestation_prirefs + item_prirefs


def get_prirefs_from_graph_exploration(start_priref: str) -> list[str]:
    unexplored_prirefs = {start_priref}
    all_prirefs = set()

    while unexplored_prirefs:
        priref = unexplored_prirefs.pop()

        if priref in all_prirefs:
            continue

        all_prirefs.add(priref)

        record = CollectRecord(collect_provider.get_by_priref(priref))

        unexplored_prirefs.update(record.get_connected_collect_prirefs())

    return list(all_prirefs)


def get_records(prirefs: list[str]) -> list[CollectRecord]:
    records = []

    for priref in prirefs:
        try:
            response = collect_provider.get_by_priref(priref)
            records.append(CollectRecord(response))
        except Exception as e:
            logger.error(
                f"Error while retrieving priref {priref}: {e}, record not collected, priref skipped"
            )
            continue

    return records


def build_repos(
    records: list[CollectRecord],
) -> tuple[PeopleRepo, ThesauRepo]:
    people_prirefs = set()
    thesau_prirefs = set()

    for record in records:
        people_prirefs.update(record.get_connected_people_prirefs())
        thesau_prirefs.update(record.get_connected_thesau_prirefs())

    people_repo = PeopleRepo()
    thesau_repo = ThesauRepo()

    people_repo.add_records(
        {
            priref: PeopleRecord(people_provider.get_by_priref(priref))
            for priref in people_prirefs
        },
    )
    thesau_repo.add_records(
        {
            priref: ThesauRecord(thesau_provider.get_by_priref(priref))
            for priref in thesau_prirefs
        },
    )
    return people_repo, thesau_repo


def translate_to_efi_records(
    records: list[CollectRecord],
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


def process_records(prirefs: list[str]):
    start = time.time()

    logging.info(f"# Retrieved {len(prirefs)} prirefs")

    records: list[CollectRecord] = get_records(prirefs)

    people_repo, thesau_repo = build_repos(records)

    efi_records = translate_to_efi_records(
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


def main():
    prirefs = get_prirefs_from_pointer_files()
    # prirefs = get_prirefs_from_graph_exploration("200339733")
    process_records(prirefs)


if __name__ == "__main__":
    main()

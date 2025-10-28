import logging
import logging.config
import logging.handlers
import os
import pathlib
import tempfile
import tomllib
from datetime import datetime

from linkml_runtime.dumpers import JSONDumper

from axiell_collections import collect_provider, pointer_file_provider
from records.record import Record

logger = logging.getLogger("collections2efi")


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    config_file = pathlib.Path("logging_config.toml")
    with open(config_file, "rb") as f_in:
        config_file = tomllib.load(f_in)
    logging.config.dictConfig(config_file)


setup_logging()


def main():
    work_prirefs = pointer_file_provider.get_by_priref(3).xpath("hit/text()")
    manifestation_prirefs = pointer_file_provider.get_by_priref(4).xpath("hit/text()")
    item_prirefs = pointer_file_provider.get_by_priref(5).xpath("hit/text()")

    prirefs = work_prirefs + manifestation_prirefs + item_prirefs

    logging.info(f"# Retrieved {len(prirefs)} prirefs")

    records = process_records(prirefs)

    logging.info(f"# Built {len(records)} records")

    purged_records = purge_records(records)

    logging.info(f"# After purge: {len(purged_records)} records")

    file_obj, json_file = tempfile.mkstemp(
        prefix=datetime.now().strftime("%Y%m%d-%H%M%S-"),
        suffix=".json",
    )
    os.close(file_obj)

    dumper = JSONDumper()
    dumper.dump(purged_records, json_file, inject_type=False)

    print(f"Wrote data to file://{json_file}")


def process_records(prirefs):
    records = []
    for priref in prirefs:
        logging.info(f"Handling record with priref {priref}")
        try:
            xml = collect_provider.get_by_priref(priref)
            record = Record(xml).build()
            records.append(record)
        except Exception as e:
            logging.error(f"Error during mapping of {priref}: {e}", exc_info=True)
            pass
    return records


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

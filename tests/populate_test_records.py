import ast
import glob
import logging
import os
import shutil

from lxml import etree

from axiell_collections import axiell_collections_database
from axiell_collections.provider import RecordProvider
from collections2efi.record import CollectRecord

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

COLLECT_DB_NAME = "collect.inf"
THESAU_DB_NAME = "thesau.inf"
PEOPLE_DB_NAME = "people.inf"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_RECORDS_BASE_PATH = SCRIPT_DIR
COLLECT_RECORDS_PATH = os.path.join(TEST_RECORDS_BASE_PATH, "test_records", "collect")
THESAU_RECORDS_PATH = os.path.join(TEST_RECORDS_BASE_PATH, "test_records", "thesau")
PEOPLE_RECORDS_PATH = os.path.join(TEST_RECORDS_BASE_PATH, "test_records", "people")

PRIREFS_TO_FETCH = [
    "200000127",
    "200000687",
    "200044362",
    "200152050",
    "200221452",
    "200236329",
    "200322007",
    "200322201",
    "200323440",
    "200339241",
]


def clear_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    logging.info(f"Cleared and recreated directory: {path}")


def save_xml(record_xml, path, priref):
    if record_xml is not None and len(record_xml):
        for element in list(record_xml):
            # remove sensitive data
            if element.tag.startswith("input") or element.tag.startswith("edit"):
                record_xml.remove(element)
                logging.info(
                    f"Removed sensitive node '{element.tag}' from record {priref}"
                )

        file_path = os.path.join(path, f"{priref}.xml")
        with open(file_path, "wb") as f:
            f.write(etree.tostring(record_xml, pretty_print=True))
        logging.info(f"Saved record {priref} to {file_path}")
    else:
        logging.warning(f"No record data to save for priref {priref}")


def main():
    collect_prirefs = PRIREFS_TO_FETCH

    logging.info(f"Found {len(collect_prirefs)} unique prirefs")

    collect_provider = RecordProvider(axiell_collections_database, COLLECT_DB_NAME)
    thesau_provider = RecordProvider(axiell_collections_database, THESAU_DB_NAME)
    people_provider = RecordProvider(axiell_collections_database, PEOPLE_DB_NAME)

    clear_directory(COLLECT_RECORDS_PATH)
    clear_directory(THESAU_RECORDS_PATH)
    clear_directory(PEOPLE_RECORDS_PATH)

    all_thesau_prirefs = set()
    all_people_prirefs = set()

    for priref in collect_prirefs:
        logging.info(f"Fetching collect record: {priref}")
        collect_xml = collect_provider.get_by_priref(priref)

        save_xml(collect_xml, COLLECT_RECORDS_PATH, priref)

        if collect_xml is not None and len(collect_xml):
            collect_record = CollectRecord(collect_xml)
            thesau_prirefs = collect_record.get_connected_thesau_prirefs()
            people_prirefs = collect_record.get_connected_people_prirefs()

            logging.info(
                f"Found {len(thesau_prirefs)} linked thesau prirefs for {priref}: {thesau_prirefs}"
            )
            logging.info(
                f"Found {len(people_prirefs)} linked people prirefs for {priref}: {people_prirefs}"
            )

            all_thesau_prirefs.update(thesau_prirefs)
            all_people_prirefs.update(people_prirefs)

    for priref in all_thesau_prirefs:
        logging.info(f"Fetching thesau record: {priref}")
        thesau_xml = thesau_provider.get_by_priref(priref)
        save_xml(thesau_xml, THESAU_RECORDS_PATH, priref)

    for priref in all_people_prirefs:
        logging.info(f"Fetching people record: {priref}")
        people_xml = people_provider.get_by_priref(priref)
        save_xml(people_xml, PEOPLE_RECORDS_PATH, priref)


if __name__ == "__main__":
    main()

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


def get_prirefs_from_tests():
    test_dirs = ["manifestations", "work", "item"]
    test_files = []
    for directory in test_dirs:
        path = os.path.join(SCRIPT_DIR, directory)
        test_files.extend(glob.glob(f"{path}/**/*.py", recursive=True))

    logging.info(f"Found test files: {test_files}")
    prirefs = set()
    for file_path in test_files:
        logging.info(f"Processing file: {file_path}")
        with open(file_path, "r") as f:
            content = f.read()
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            if (
                                isinstance(decorator, ast.Call)
                                and isinstance(decorator.func, ast.Attribute)
                                and isinstance(decorator.func.value, ast.Attribute)
                                and decorator.func.value.value.id == "pytest"
                                and decorator.func.value.attr == "mark"
                                and decorator.func.attr == "parametrize"
                            ):
                                if (
                                    len(decorator.args) > 1
                                    and isinstance(decorator.args[0], ast.Constant)
                                    and "priref" in decorator.args[0].value
                                ):
                                    if isinstance(
                                        decorator.args[1], (ast.List, ast.Tuple)
                                    ):
                                        for element in decorator.args[1].elts:
                                            if isinstance(
                                                element, (ast.List, ast.Tuple)
                                            ):
                                                if len(element.elts) > 0 and isinstance(
                                                    element.elts[0], ast.Constant
                                                ):
                                                    prirefs.add(
                                                        str(element.elts[0].value)
                                                    )
            except Exception as e:
                logging.error(f"Error parsing {file_path}: {e}")

    return list(prirefs)


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
    collect_prirefs = get_prirefs_from_tests()
    if not collect_prirefs:
        logging.warning("No prirefs found in test files. Exiting.")
        return

    logging.info(
        f"Found {len(collect_prirefs)} unique prirefs in test files: {collect_prirefs}"
    )

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

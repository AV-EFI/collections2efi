import json
import logging

from axiell_collections import axiell_collections_database
from axiell_collections import Cursor

logging.getLogger("dicttoxml").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

FILE_PATH = "lieferung-250304-journal-1.json"
AXIELL_COLLECTIONS_DB_NAME = "collect.inf"

# TODO add host !


def process_record(record, cursor):
    local_id = record.get("local_id")
    action = record.get("action")
    pid = record.get("pid")

    logging.info(f"Processing record local_id: {local_id}")

    if action != "CREATE":
        logging.info(f"Skipping record {local_id} with action '{action}' (not CREATE)")
        return

    try:
        update_payload_data = {
            "PID_data_URI": pid,
        }

        response = cursor.update_record(
            priref=local_id,
            database=AXIELL_COLLECTIONS_DB_NAME,
            data=update_payload_data,
        )

        if response.error:
            raise Exception("Update did not work")

        logging.info(f"Successfully updated record {local_id} with PID: {pid}")

    except Exception as e:
        logging.error(f"Error processing record {local_id}: {e}")


def main():
    try:
        cursor = Cursor(axiell_collections_database)

        with open(FILE_PATH, "r", encoding="utf-8") as f:
            records = json.load(f)

        for i, record in enumerate(records):
            logging.info(f"{i+1}/{len(records)}")
            process_record(record, cursor)

    except FileNotFoundError:
        logging.error(f"Error: The file '{FILE_PATH}' was not found.")

    except json.JSONDecodeError:
        logging.error(
            f"Error: Could not decode JSON from '{FILE_PATH}'. Check file format."
        )

    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

# collections2efi

Code to transform Axiell Collections records into [av-efi-schema](https://github.com/AV-EFI/av-efi-schema) compliant records. 

## Installation

For installation, you need
- Python >=3.11 and 
- [Poetry](https://python-poetry.org)

installed. Run 

```bash
git clone https://github.com/your-org/av-efi-generator.git
cd av-efi-generator
```

to clone the repository and

```bash
poetry install
```

to install all dependencies.

## Configuration

Two key files define translation logic:
- [`src/collections2efi/record_definitions.toml`](./src/collections2efi/record_definitions.toml) maps av-efi-schema class values to python translation functions.
- [`src/collections2efi/mappings/mappings.toml`](./src/collections2efi/mappings/mappings.toml) defines the vocabulary mapping from collections to AV-EFI enums.

The system supports simple mappings (direct XPath to Enum) and complex mappings (delegated to functions in [`src/collections2efi/record_type/`](./src/collections2efi/record_type/)).

## Package Architecture

The library relies on three main components to orchestrate the translation:

- Records: Wrappers around raw XML data that provide helper methods for traversing relationships.
  - `CollectRecord`: The primary record (Work, Manifestation, Item).
  - `PeopleRecord` & `ThesauRecord`: Auxiliary context for persons and thesaurus terms.
- Repositories: In-memory stores (`PeopleRepo`, `ThesauRepo`) for the auxiliary records, working as a cache.
- Translator: The core logic that applies the configured mappings. It combines a `CollectRecord` with data from the repositories to produce an AV-EFI object.



## Scripts in the project

### [`main.py`](./main.py)

This script demonstrates a fetch-translate-purge cycle. 

Ensure the `SDK_AXIELL_COLLECTIONS_URL` environment variable is set.

Ensure the `SDK_AXIELL_COLLECTIONS_CACHED` environment variable is set. See [Caching](#caching)

```bash
export SDK_AXIELL_COLLECTIONS_URL=http://...
poetry run python main.py
```

Process Flow:
1. Fetch: Retrieves records
    - via pointer files
    - via direct input
    - via subgraph exploration on direct input
2. Contextualize: Fetches and "caches" related people and thesaurus records.
3. Translate: Converts records using the `Translator`.
4. Purge: Removes orphan records (records without valid parents).
5. Output: Writes the final JSON to the `tmp` directory.

### [`write_pids.py`](./main.py)

This temporary script provides an outline on how PIDs could be written back into collections.

## Caching

During development, it was very helpful to have the requests to the axiell collections database cached.
This was done very rudimentarily by using the package [`requests-cache`](https://requests-cache.readthedocs.io/en/stable/).

For caching set `SDK_AXIELL_COLLECTIONS_CACHED = 1`.

_Note: There is no cache invalidation implemented, to invalidate delete the generated `axiell_collections_cache.sqlite` database._

## Testing

Regression tests in [`./tests/test_complete_records.py`](./tests/test_complete_records.py) verify output against known states stored in [`./tests/test_complete_records`](./tests/test_complete_records).

Unit tests for the specific mappings functions are located in the folders [work](./tests/work), [manifestation](./tests/manifestation), and [item](./tests/item). At this point they are very incomplete.

Update and run [populate_test_records.py](./tests/populate_test_records.py) with required records before running tests.

```bash
poetry run pytest
```

*Note: Sensitive data (like names) is redacted from stored files for privacy.*

## Linting and Formatting

Code quality is enforced via [ruff](https://docs.astral.sh/ruff/).

- Lint with 
  ```bash
  poetry run ruff check --fix
  ```
- Format with
  ```bash
  poetry run ruff format
  ```
## Updating to a new AVEFI version

To upgrade the schema, update the git commit hash in [pyproject.toml](./pyproject.toml) and run:

```bash
poetry update avefi-schema
poetry install
```

## Logging

Structured logging is configured in [`logging_config.toml`](./logging_config.toml) and writes to [`logs/`](./logs/). Use these logs to monitor:
- Mapping errors and data inconsistencies.
- API connectivity issues.
- Processing statistics (counts, purges).

# Publishers export

This script gets all publishers from DiVA Classic database and saves them to an XML file, that can be imported using the [`publishers-import`](./publishers_import.md) script.

> **Note:** Export and import are combined in the `diva-migrate` command. See `diva-migrate --help`.

The output is saved to `data/db_xml/publishers_{TIMESTAMP}.xml`

## Prerequisites

- Python 3 and PIP installed
- A `.env` file configured with database connection settings (see [README](../README.md#configuration)), or pass `--db-host`, `--db-user`, `--db-password` as CLI arguments
- You must have read access to the DiVA Classic database

## Installing the package

```bash
pip install .
```

## Running the script

```bash
publishers-export
```

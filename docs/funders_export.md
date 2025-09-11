# Funders export

This script gets all funders from DiVA Classic database and saves them to an XML file, that can be imported using the [`funders-export`](./funders_export.md) script.

The output is saved to `data/db_xml/funders_{TIMESTAMP}.xml`

## Prerequisites

- Python 3 and PIP installed
- You must be on the UUB network
- Your SSH public key must be added to the SSH agent
- You must have read access to the DiVA Classic database

## Installing the package

```bash
pip install .
```

## Running the script

```bash
funders-export
```

You will be prompted for the database username and password.

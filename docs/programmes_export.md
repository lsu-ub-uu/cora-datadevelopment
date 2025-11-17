# Programmes export

This script gets all programmes from DiVA Classic database and saves them to an XML file, that can be imported using the [`programmes-import`](./programmes_import.md) script.

The output is saved to `data/db_xml/programmes_{TIMESTAMP}.xml`

## Prerequisites

- Python 3 and PIP installed
- Your SSH public key must be added to the SSH agent
- You must have read access to the DiVA Classic database

## Installing the package

```bash
pip install .
```

## Running the script

```bash
programmes-export --domain someDomain
```

You will be prompted for the database username and password.

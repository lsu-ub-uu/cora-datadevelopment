# Series export

This script gets all series from DiVA Classic database and saves them to an XML file, that can be imported using the [`series-export`](./series_export.md) script.

The output is saved to `data/db_xml/series_{TIMESTAMP}.xml`

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
series-export --domain someDomain
```

You will be prompted for the database username and password.

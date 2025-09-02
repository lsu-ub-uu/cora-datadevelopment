# Publishers import

This script imports publishers from XML files exported from Diva Classic database, transforms them to Cora format and imports them to the specified DiVA Cora system.

## Prerequisites

- Python 3 and PIP installed
- An XML file with exported publishers from DiVA Classic Database

### Example source XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
    <DATA_RECORD>
        <old_id>8204</old_id>
        <name>The Society for the Study of Ethnic Relations and International Migration (ETMU)</name>
    </DATA_RECORD>
    <DATA_RECORD>
        <old_id>55</old_id>
        <name>Blackwell Publishing</name>
    </DATA_RECORD>
</SELECT_p_publishing_house_id_as_old_id_p_name_FROM_publishing_house_p>
```

## Installing the package

```bash
pip install .
```

## Running the script (dry run)

```bash
publishers-import --xml-path path/to/publishers.xml --system mig
```

## Running the script and create records in Cora

```bash
publishers-import --xml-path path/to/publishers.xml --system mig --apply
```

## Show script help, with all available parameters

```bash
publishers-import --help
```

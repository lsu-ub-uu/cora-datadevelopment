# Funder import

This script imports funders from XML files exported from Diva Classic database, transforms them to Cora format and imports them to the specified DiVA Cora system.

## Prerequisites

- Python 3 and PIP installed
- An XML file with exported funders from DiVA Classic Database

### Example source XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SELECT>
  <DATA_RECORD>
    <old_id>103</old_id>
    <name_swe>Sida - Styrelsen för internationellt utvecklingssamarbete</name_swe>
    <name_eng>Sida - Swedish International Development Cooperation Agency</name_eng>
    <end_date></end_date>
    <identifier_organisationNumber>202100-4789</identifier_organisationNumber>
    <identifier_doi>10.13039/100004441</identifier_doi>
    <locale_swe>sv</locale_swe>
    <locale_eng>en</locale_eng>
    <funder_name_id>15</funder_name_id>
  </DATA_RECORD>
</SELECT>
```

## Installing the package

```bash
pip install .
```

## Running the script (dry run)

```bash
funders-import --xml-path path/to/funders.xml --system mig
```

## Running the script and create records in Cora

```bash
funders-import --xml-path path/to/funders.xml --system mig --apply
```

## Show script help, with all available parameters

```bash
funders-import --help
```

# Journals import

This script imports journals from XML files exported from Diva Classic database, transforms them to Cora format and imports them to the specified DiVA Cora system.

## Prerequisites

- Python 3 and PIP installed
- An XML file with exported journals from DiVA Classic Database

### Example source XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SELECT>
	<DATA_RECORD>
		<old_id>12505</old_id>
		<title>Journal of Development Economics</title>
		<subtitle />
		<end_date />
		<identifier_eissn>1872-6089</identifier_eissn>
		<identifier_pissn>0304-3878</identifier_pissn>
		<url />
	</DATA_RECORD>
</SELECT>
```

## Installing the package

```bash
pip install .
```

## Running the script (dry run)

```bash
journals-import --xml-path path/to/journals.xml --system mig
```

## Running the script and create records in Cora

```bash
journals-import --xml-path path/to/journals.xml --system mig --apply
```

## Show script help, with all available parameters

```bash
journals-import --help
```

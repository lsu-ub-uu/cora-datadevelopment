# Subjects import

This script imports subjects from XML files exported from Diva Classic database, transforms them to Cora format and imports them to the specified DiVA Cora system.

## Prerequisites

- Python 3 and PIP installed
- An XML file with exported subjects from DiVA Classic Database

## Limitations

- Does not support links between subjects (`broader_id`, `parent_subject_id`, `earlier_id`)

### Example source XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SELECT>
	<DATA_RECORD>
		<domain>varldskulturmuseerna</domain>
		<old_id>40103</old_id>
		<end_date></end_date>
		<name_swe>Digital humaniora</name_swe>
		<name_eng>Digital humaniora</name_eng>
		<broader_id></broader_id>
		<parent_subject_id></parent_subject_id>
		<earlier_id></earlier_id>
  	</DATA_RECORD>
</SELECT>
```

## Installing the package

```bash
pip install .
```

## Running the script (dry run)

```bash
subjects-import --xml-path path/to/subjects.xml --system mig
```

## Running the script and create records in Cora

```bash
subjects-import --xml-path path/to/subjects.xml --system mig --apply
```

## Show script help, with all available parameters

```bash
subjects-import --help
```

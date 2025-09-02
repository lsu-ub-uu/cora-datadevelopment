# Series import

This script imports series from XML files exported from Diva Classic database, transforms them to Cora format and imports them to the specified DiVA Cora system.

## Prerequisites

- Python 3 and PIP installed
- An XML file with exported series from DiVA Classic Database

## Limitations

- Does not support links between series (`relative_id_host`, `relative_id_preceding`)
- Does not support links to organisations (`organisation_id`)

### Example source XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SELECT>
<DATA_RECORD>
		<domain>smhi</domain>
		<old_id>12556</old_id>
		<title>RO, Rapport Oceanografi</title>
		<subTitle></subTitle>
		<alternative_title>RO, Report Oceanography</alternative_title>
		<alternative_sub_title></alternative_sub_title>
		<end_date></end_date>
		<identifier_pissn>0283-1112</identifier_pissn>
		<identifier_eissn></identifier_eissn>
		<url></url>
		<external_note></external_note>
		<publication_type_id></publication_type_id>
		<relative_id_host></relative_id_host>
		<relative_id_preceding></relative_id_preceding>
		<organisation_id></organisation_id>
	</DATA_RECORD>
</SELECT>
```

## Installing the package

```bash
pip install .
```

## Running the script (dry run)

```bash
series-import --xml-path path/to/series.xml --system mig
```

## Running the script and create records in Cora

```bash
series-import --xml-path path/to/series.xml --system mig --apply
```

## Show script help, with all available parameters

```bash
series-import --help
```

# DiVA migrate

This script migrates data from DiVA Classic to DiVA on Cora for a given domain. It can optionally migrate shared common data (publishers, funders, journals) as well as domain-specific data (organisations, subjects, series, programmes, courses).

## Prerequisites

- Python 3 and PIP installed
- A `.env` file configured with the Classic database and Cora connection settings (see [README](../README.md#configuration)), or pass them as CLI arguments

## Installing the package

```bash
pip install .
```

## Running the script

```bash
diva-migrate --domain someDomain --system minikube
```

## Migrating common data

Common data (publishers, funders, journals) is shared across domains and is skipped by default. Include it with `--include-common-data`:

```bash
diva-migrate --domain someDomain --system minikube --include-common-data
```

## Migrating specific record types

By default all record types are migrated. Restrict the migration to specific types with `--record-types`, a comma-separated list from: `publishers`, `funders`, `journals`, `organisations`, `subjects`, `series`, `programmes`, `courses`.

```bash
diva-migrate --domain someDomain --system minikube --record-types organisations,subjects
```

## Show script help, with all available parameters

```bash
diva-migrate --help
```

# Outputs export

This script gets all publications for a domain from DiVA Classic, using Solr and Fedora and saves them as XML files.

## Prerequisites

- Python 3 and PIP installed
- A `.env` file configured with `FEDORA_URL` and `SOLR_URL` (see [README](../README.md#configuration)), or pass them as CLI arguments

## Installing the package

```bash
pip install .
```

## Running the script (dry run)

```bash
outputs-export --domain someDomain
```

## Show script help, with all available parameters

```bash
outputs-export --help
```

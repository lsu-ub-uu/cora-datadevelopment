# Organisations migrate

This script gets organisations from all domains in DiVA Classic (Cora), transforms them to the new DiVA Cora format, creates them in new DiVA on Cora, and finally updates the records with relations between organisations. Root organisations are excluded.

Source organisations are fetched automatically in pages of 1,000 records, with no overall record limit. All pages are fetched before any records are created.

## Prerequisites

- Python 3 and PIP installed

## Installing the package

```bash
pip install .
```

## Running the script

To migrate organisations from all domains:

```bash
organisations-migrate --system minikube
```

To migrate organisations only for a specific domain, supply the optional `--domain` argument:

```bash
organisations-migrate --system minikube --domain someDomain
```

## Show script help, with all available parameters

```bash
organisations-migrate --help
```

# Organisations migrate

This script gets all organisations for a domain from DiVA Classic (Cora), transforms them to the new DiVA Cora format, creates them in new DiVA on Cora, and finally updates the records with relations between organisations.

## Prerequisites

- Python 3 and PIP installed

## Installing the package

```bash
pip install .
```

## Running the script

```bash
outputs-migrate --system minikube --domain someDomain
```

## Show script help, with all available parameters

```bash
outputs-migrate --help
```

# Outputs export

This script gets all publications for a domain from DiVA Classic, using Solr and Fedora and saves them as XML files.

## Prerequisites

- Python 3 and PIP installed
- You must be on the UUB network
- Your SSH public key must be added to the SSH agent

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

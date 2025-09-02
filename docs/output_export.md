# Publishers import

This script imports publishers from XML files exported from Diva Classic database, transforms them to Cora format and imports them to the specified DiVA Cora system.

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

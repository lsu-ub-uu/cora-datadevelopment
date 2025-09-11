# Cora data development

This repository contains scripts for creating and migrating data.

## Data migration scripts for Classic DiVA to Cora DiVA

### Publishers

- [Publisher export](docs/publishers_export.md)
- [Publisher import](docs/publishers_import.md)

### Funders

- [Funder import](docs/funders_import.md)
- [Funder export](docs/funders_export.md)

### Journals

- [Journal import](docs/journals_import.md)
- [Journal export](docs/journals_export.md)

### Subjects

- [Subject export](docs/subjects_export.md)
- [Subject import](docs/subjects_import.md)

### Series

- [Series export](docs/series_export.md)
- [Series import](docs/series_import.md)

### Outputs

- [Outputs export](docs/outputs_export.md)
- [Outputs import](docs/outputs_import.md)

## Development

### Dev installation

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run tests

```sh
pytest
```

### Run tests with coverage report

```sh
pytest --cov=src
```

### Run tests in watch mode

```sh
ptw --now .
```

For more information about output migration, see [here](./src/fedora_to_cora/transform/output_transform.md)

`outputs-testdata-create` to create a dummy post in the Cora format, it uses the same arguments but does not include the `--apply` and always creates a post.

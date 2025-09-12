# Cora data development

This repository contains scripts for creating and migrating data.

## Data migration scripts for Classic DiVA to Cora DiVA

### Publishers

- [Publisher export from Classic](docs/publishers_export.md)
- [Publisher import to Cora](docs/publishers_import.md)

### Funders

- [Funder import from Classic](docs/funders_import.md)
- [Funder export to Cora](docs/funders_export.md)

### Journals

- [Journal export from Classic](docs/journals_export.md)
- [Journal import to Cora](docs/journals_import.md)

### Subjects

- [Subject export from Classic](docs/subjects_export.md)
- [Subject import to Cora](docs/subjects_import.md)

### Series

- [Series export from Classic](docs/series_export.md)
- [Series import to Cora](docs/series_import.md)

### Outputs

- [Outputs export from Classic](docs/outputs_export.md)
- [Outputs import to Cora](docs/outputs_import.md)

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

# Cora data development

This repository contains scripts for creating and migrating data.

## Scripts

- [Publisher import](docs/publishers_import.md)
- [Funder import](docs/funders_import.md)
- [Journal import](docs/journals_import.md)
- [Subject import](docs/subjects_import.md)
- [Series import](docs/series_import.md)
- [Organisations import](docs/organisations_import.md)
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

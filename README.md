# Cora data development

This repository contains scripts for creating and migrating data.

## Dev installation

```sh
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Run tests

```sh
pytest
```

## Run tests with coverage report

```sh
pytest --cov=src
```

## Run tests in watch mode

```sh
ptw --now .
```

## Run scripts

`output-migrate` to migrate posts with the fedora format into the Cora format

- `-h`, `--help`: show the helper
- `--xml-dir`: the directory where the fedora XML publications are located.
- `--system`: the system where you want to put the migrated posts.
- `--login-id`: the id for the user used to migrate the posts.
- `--app-token`: the token for the user.
- `--wet-run`: if you want to do a dry-run of the script without creating the migrated files.

For more information about output migration, see [here](./src/fedora_to_cora/transform/output_transform.md)

`output-testdata-create` to create a dummy post in the Cora format, it uses the same arguments but does not include the `--wet-run` and always creates a post.

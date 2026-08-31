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

### Organisations

- [Organisations migrate from Classic Cora to New Cora](docs/organisations_migrate.md)

### Outputs

- [Outputs export from Classic](docs/outputs_export.md)
- [Outputs import to Cora](docs/outputs_import.md)

### Common record type scripts

- Publisher
- Funder
- Journal
- Person
- Project

### Member specific scripts

- Subject
- Organisation
- Course
- Programme
- Series
- Output

### Migration order

1.  - Publishers (no references)
    - Funders (no references)
    - Journals (no references)
2.  - Organisations (references organisations)
    - Courses (references courses)
    - Programmes (references programmes)
    - Subjects (references subjects)
3.  - Persons (references organisations)
    - Series (references organisations)
4.  - Projects (refefrences persons, organisatoions, funders, subjects)
5.  - Outputs (references all the other types and outputs)

## Configuration

All scripts read configuration from CLI arguments, environment variables, or a `.env` file (in that priority order).

### Setting up `.env`

```sh
cp .env.example .env
```

Edit `.env` with your values:

```env
CORA_SYSTEM=preview
CORA_LOGIN_ID=divaAdmin@cora.epc.ub.uu.se
CORA_APP_TOKEN=your-token-here
CORA_WORKERS=16

FEDORA_URL=http://fedora-host:8088
SOLR_URL=http://solr-host:8083/solr-admin/dream/select

DB_HOST=diva-storage1
DB_PORT=5432
DB_NAME=auradb
DB_USER=your-db-user
DB_PASSWORD=your-db-password
```

Any value set in `.env` can be overridden by passing the corresponding CLI argument (e.g. `--system production`).

## Docker

### Build

```sh
docker build -t cora-datadevelopment .
```

### Run

Bind-mount `data/`, `logs/`, `output_xml/`, and `reports/` so artifacts persist between runs:

```sh
docker run \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  -v ./output_xml:/app/output_xml \
  -v ./reports:/app/reports \
  --env-file .env \
  cora-datadevelopment <command> [args]
```

For example:

```sh
docker run \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  --env-file .env \
  cora-datadevelopment outputs-export --domain uu
```

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

To get full diffs for large XML comparisons, run tests with flag `-vvv`

`outputs-testdata-create` to create a dummy post in the Cora format, it uses the same arguments but does not include the `--apply` and always creates a post.

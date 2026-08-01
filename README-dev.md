# ipref-py (for Developers)

This is a README for developers.
It describes the technology stack, how to set up the development environment,
coding conventions, and other development-specific documentation.

For how to contribute (bug reports, feature requests, and pull requests), see
[CONTRIBUTING.md](CONTRIBUTING.md).


## Development tools

- Language: Python 3.9 or later
- Package manager: `uv` (https://docs.astral.sh/uv/)
- Formatter: `ruff` (https://docs.astral.sh/ruff/)
- Linter: `ruff` (https://docs.astral.sh/ruff/)
- Type checker: `ty` (https://docs.astral.sh/ty/)
- Test framework: `pytest` (https://docs.pytest.org/en/stable/index.html)
    - pytest extensions: `pytest-cov`, `pytest-mock`
- CI/CD framework: GitHub Actions


## Coding conventions

This project basically follows the coding conventions below.

- Python code: `ruff` is used as the formatter and the linter.
    - PEP 8: https://peps.python.org/pep-0008/
    - Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
    - Ruff Documentation: https://docs.astral.sh/ruff/
- Docstrings: Google-style comments.
    - Google Python Style Guide: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
- Type hints: Use type hints available in Python 3.9. `ty` is used as the
  type checker.
    - ty Documentation: https://docs.astral.sh/ty/


## Directory structure

This project uses the flat layout.

- `.claude/`: Claude Code settings **(not tracked)**
- `.devcontainer/`
    - `devcontainer.example.json`: Template of the DevContainer configuration
    - `devcontainer.json`: DevContainer configuration **(not tracked)**
- `.github/`
    - `ISSUE_TEMPLATE/`: Issue templates
    - `PULL_REQUEST_TEMPLATE/`: Pull request templates
    - `workflows/`: GitHub Actions workflows (`test.yml`, `release.yml`)
    - `copilot-instructions.md`: GitHub Copilot instructions
    - `dependabot.yml`: Dependabot configuration
- `.venv/`: virtualenv environment (used by `uv`) **(not tracked)**
- `etc/`: Configuration file templates for deployment
    - `ipref-web.service`: systemd unit file template
    - `nginx.conf`: nginx configuration template (reverse proxy)
- `ipref/`: Main package
    - `data/`: Lookup modules (GeoIP, DNS)
    - `static/`, `templates/`: Web interface assets
    - `config.yaml.orig`, `config-geolite.yaml.orig`: Configuration templates
    - `__main__.py`: CLI entry point
    - `web.py`: Web app (Flask)
- `tests/`: Test scripts
    - `data/`: Test databases (MaxMind test data)
    - `etc/`: Test configurations
    - `conftest.py`: Common code for `pytest`
- `.gitignore`
- `.goreleaser.yml`
- `AGENTS.md`: Instructions for AI coding agents
- `CHANGELOG.md`
- `LICENSE`
- `Makefile.example`: Template of the task Makefile
- `README.md`
- `pyproject.toml`
- `requirements-dev.txt`: Snapshot of the libraries for development/testing
- `requirements.txt`: Snapshot of the libraries for runtime
- `uv.lock`: Lock file of `uv`


## Development environment

Set up the development environment with the following steps.

The following two environments are supported:

- Local environment:
    - Develop and run tests on your local machine.
- DevContainer environment (w/ VSCode):
    - Develop and run tests inside a docker container.

In both environments, the development tasks are defined in `Makefile.example`.


### Local environment

`uv` is used as the package manager, so install it first:

https://docs.astral.sh/uv/getting-started/installation/

Create a `Makefile`:

```sh
$ cp -vi Makefile.example Makefile
```

Install the libraries for development with `uv`:

```sh
$ make install-dev
```


### DevContainer environment

Install VSCode and the Dev Containers extension of VSCode.

Create a `devcontainer.json` and a `Makefile`:

```sh
# Copy the DevContainer configuration and edit it for your environment if
# necessary. devcontainer.json is not tracked by git.
$ cp -vi .devcontainer/devcontainer.example.json .devcontainer/devcontainer.json

$ cp -vi Makefile.example Makefile
```

Run "Dev Containers: Rebuild and Reopen in Container" from the command
palette of VSCode.

The libraries for development are installed automatically
(`uv sync --all-extras --dev`).


## Tasks

### Build

The build basically runs on GitHub Actions (CI/CD environment), so you do not
need to run it locally.

To build the package manually, use the following command:

```sh
$ make build
```

To update `requirements.txt` and `requirements-dev.txt`, run the following
command:

```sh
$ make freeze
```


### Formatter / Linter / Type checker

`ruff` is used as the formatter and the linter, and `ty` is used as the type
checker.

To run them manually, use the following commands:

```sh
# Check the format
$ make format

# Apply the formatter
$ make format-fix

# Check the lint
$ make lint

# Apply lint fixes
$ make lint-fix

# Type check
$ make typecheck
```


### Unit tests

`pytest` is used for unit tests.

To run them manually, use the following command:

```sh
$ make test
```

Some tests use MaxMind's test databases in `tests/data/`.


### Development server (web interface)

To run the Flask development server for the web interface, use the following
command:

```sh
# Set the IPREF_CONF environment variable to your configuration file if
# necessary.
$ make serve
```

The server listens on http://localhost:5000/ by default.
Do NOT use this server in production (see README.md for production
deployment with gunicorn).


### Version update

To update the package version, use the following commands:

```sh
# You can check the result with --dry-run.
$ uv version --bump major   # X in X.Y.Z
$ uv version --bump minor   # Y in X.Y.Z
$ uv version --bump patch   # Z in X.Y.Z
```

Note that rc (release candidate) versions are not used in this project
because the version string formats of PEP and Semantic Versioning differ and
the build workflows do not work with the PEP format.

**Note**: The version number is managed only in the `project.version` field in
`pyproject.toml`. `ipref.__version__` is resolved at runtime from the package
metadata.


## CI/CD

Tests and packaging are automated with GitHub Actions.


### Tests

The test workflow is [.github/workflows/test.yml](.github/workflows/test.yml).

It runs on pushes and pull requests, and also periodically (because dependent
packages may be updated). The following tasks are executed:

- `ruff`: formatter
- `ruff`: linter
- `ty`: type checker
- Check that `--help` and `--version` work
- `pytest`


### Dependency updates (Dependabot)

The Dependabot configuration is
[.github/dependabot.yml](.github/dependabot.yml).

It checks the dependencies of GitHub Actions and `uv` weekly, and creates
pull requests against the `develop` branch.

- Merge the pull requests with **Squash and merge** after the CI passes.
- **Note**: For updates of transitive dependencies, Dependabot rewrites only
  `requirements.txt` / `requirements-dev.txt` and does not update `uv.lock`.
  After the merge, update `uv.lock` and regenerate the snapshots with the
  following commands:

```sh
$ uv lock --upgrade
$ make freeze
```


### Packaging

The packaging workflow is
[.github/workflows/release.yml](.github/workflows/release.yml).

When a pull request is merged (strictly speaking, closed) into the `main`
branch or a `release/v*` branch, the following tasks are executed:

- Version check:
    - If the version is an rc, the workflow stops there.
    - If the version is already tagged, the workflow stops there (it continues
      only for new versions).
- Tagging: The version is added as a git tag.
- Build: The package is built with `uv build`.
- Release: The package is registered to GitHub Releases with GoReleaser.

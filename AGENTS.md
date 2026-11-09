# AGENTS.md

Guidance for AI coding agents working in this repository.

## Overview

Django 6.0 (Python 3.14) application serving the data.gov.uk website. Dependencies are managed with `uv`; local development runs in Docker via `docker-compose.local.yml`.

Further developer docs live in `docs/` (CI/CD pipeline, ECS deployment, feature flags, frontend, testing).

## Commands

All project commands use `just` (`brew install just`). Run `just` alone to list them.

```bash
just init          # First-time setup: installs uv and pre-commit, copies the overrides envfile, brings up containers
just up            # Start Docker containers (app at localhost:8000)
just down          # Stop containers
just build         # Rebuild the Docker image
just logs          # Tail container logs
just bash          # Shell into the Django container
just manage <cmd>  # Run manage.py commands (e.g. just manage check)
```

### Testing

Tests run inside the Docker container, so `just up` first.

```bash
just test                        # Run all tests in parallel (pytest -n auto)
just test datagovuk/core/tests/  # Run a specific test directory
just test -k test_my_function    # Run tests matching a name pattern
just test-unit                   # Unit/view tests only (datagovuk/)
just test-e2e                    # Playwright e2e tests only (tests/e2e/)
just coverage                    # Unit tests with an HTML coverage report
```

CI fails if unit test coverage of `datagovuk/` drops below 100%.

To debug e2e tests on the host instead of in Docker:

```bash
just e2e-install-playwright   # One-time: install Playwright browsers
just e2e-debug tests/e2e/     # Run with PWDEBUG=1
just e2e-codegen <file>       # Record a new test with the Playwright recorder
```

### Linting

```bash
just lint --all-files   # Run all pre-commit hooks
```

Hooks include Ruff check and format (120-char line limit, broad rule set in `pyproject.toml`), djLint for Jinja templates, django-upgrade (targeting Django 6.0) and pyproject-fmt.

### Static assets

```bash
just compress      # Compress CSS/JS referenced by {% compress %} tags
just collectstatic # Collect static files for non-local environments
```

## Architecture

- **Templates**: Jinja2, not Django's default engine. Each app keeps its templates in its own `jinja2/` directory (e.g. `datagovuk/core/jinja2/`). Template files use the `.jinja` extension.
- **Content**: Markdown files with YAML front matter under `datagovuk/content/`, parsed with `python-frontmatter` and rendered with `mistune`.
- **Static files**: In `datagovuk/static/`. SCSS is compiled by `django-compressor` + `django-libsass`; WhiteNoise serves files in production.
- **Settings**: Split by environment under `config/settings/` (`base.py`, `local.py`, `production.py`, `test.py`, `heroku.py`). Environment variables are loaded via `django-environ`.
- **Local env vars**: Shared defaults are committed in `.envs/.local/.django`; personal overrides go in `.envs/.local/.django-overrides` (not committed).
- **Feature flags**: Defined in the `FEATURE_FLAGS` enum in `config/settings/base.py`. Use sparingly and remove once a feature is permanently on. See `docs/feature_flags.md`.

Django apps under `datagovuk/`:

- `core` — shared utilities, middleware, context processors, markdown rendering, feature flags
- `pages` — static/content pages
- `collections` — dataset collections
- `data_manual` — data manual content
- `directory` — dataset search and dataset pages, backed by Solr
- `support` — support form, which creates Zendesk tickets
- `ckan_redirect` — redirects from legacy CKAN URLs

## Testing conventions

See `docs/testing.md` for detail. Tests sit next to the code in `tests/` subdirectories; e2e tests are in `tests/e2e/`.

- **Unit tests**: Mirror the structure of the code under test, e.g. `class CollectionService` → `class TestCollectionService`, `def render_markdown` → `def test_render_markdown_...`. Test names should describe the thing under test, the state and the expected behaviour (be pragmatic).
- **Django view tests**: Use Django's test client; treat these as integration tests. For HTML responses, assert on the template context rather than the raw HTML.
- **E2E tests**: Playwright. They should simulate real user interactions.

## Frontend conventions

See `docs/frontend.md` for detail.

- GOV.UK Frontend is the base design system.
- Use BEM notation with the `datagovuk-` prefix for all custom classes.
- Style elements through classes only, never with element selectors.
- To override a GOV.UK style, add a `datagovuk-[name]` class in `datagovuk/static/stylesheets/overrides/` and apply it alongside the original `govuk-*` class.
- Style mobile first, with media queries for larger screens.
- Use progressive enhancement.

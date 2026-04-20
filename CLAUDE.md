# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All project commands use `just` (install with `brew install just`). Run `just` alone to list available commands.

```bash
just init          # First-time setup: installs uv, pre-commit, copies envfile, initialises submodules
just up            # Start Docker containers (app at http://localhost:8000)
just down          # Stop containers
just build         # Rebuild Docker image
just logs          # Tail container logs
just bash          # Shell into the Django container
just manage <cmd>  # Run manage.py commands (e.g. just manage migrate)
```

### Testing

```bash
just test                        # Run all tests with coverage (requires 100%)
just test datagovuk/core/tests/  # Run a specific test directory
just test -k test_my_function    # Run tests matching a name pattern
```

E2E tests (Playwright) run locally, not in Docker:
```bash
just e2e-install-playwright   # Install Playwright browsers (first time)
uv run pytest tests/e2e/      # Run e2e tests
just e2e-debug tests/e2e/     # Run in debug mode (PWDEBUG=1)
```

### Linting

```bash
just lint                        # Run all pre-commit hooks
pre-commit run --all-files       # Equivalent full run
```

Linting enforces: Ruff (120-char line limit), djLint (Jinja2 templates), django-upgrade (targeting Django 6.0).

### Static assets

```bash
just compress      # Compress CSS/JS referenced by {% compress %} tags
just collectstatic # Collect static files for non-local environments
```

## Architecture

Django 6.0 application serving the data.gov.uk website. Key characteristics:

- **Templates**: Jinja2 (not Django's default template engine). Templates live in `datagovuk/templates/`.
- **Content**: Markdown files with YAML front matter, parsed via `python-frontmatter` and rendered with `mistune`.
- **Static files**: Served by WhiteNoise in production; `django-compressor` + `django-libsass` for SCSS compilation.
- **Settings**: Environment-split under `config/settings/` (`base.py`, `local.py`, `production.py`, `test.py`). Env vars loaded via `django-environ`.
- **Git submodule**: `datagovuk_find/` is a separate Ruby/Rails application (alphagov/datagovuk_find). Keep it updated with `git submodule update --remote`.

Django apps under `datagovuk/`:
- `core` — shared utilities and base functionality
- `pages` — static/content pages
- `collections` — dataset collection management
- `data_manual` — data manual content

## Testing conventions

100% coverage is enforced in CI. Tests are co-located with code in `tests/` subdirectories.

- **Unit tests**: Mirror source structure. `class CollectionService` → `class TestCollectionService`. Test method names should describe the thing under test, state, and expected behaviour.
- **Django view tests**: Use Django's test client; treat as integration tests. For HTML responses, assert on template context rather than raw HTML.
- **E2E tests**: Playwright tests in `tests/e2e/`. Simulate real user interactions.

## Frontend conventions

- GOV.UK Frontend design system as base.
- BEM CSS notation with `datagovuk-` prefix for all custom classes.
- Style elements via classes only, never direct element selectors.
- Overrides go in `stylesheets/v2/overrides/` as `datagovuk-[name]` classes alongside the original `govuk-*` class.
- Mobile-first with media queries for larger screens.
- Progressive enhancement approach.

# Our GitHub Actions Workflows

1. build-image.yaml
2. ci.yaml
3. create-integration-pr.yaml
4. trivy-scans.yaml

## On Pull request

It runs the `ci.yaml` and `trivy-scans.yaml` workflows.

### CI Workflow

It runs these jobs:

- Linting
- CodeQL (SAST)
- Django tests (unit, view and end-to-end)

### Trivy vulnerability scans

The trivy-scans.yaml runs vulnerability scans on our dependencies and fails when CRITICAL or HIGH CVEs are found.

## On merge to main branch

It runs these workflows:

1. ci.yaml
2. trivy-scans.yaml
3. build-image.yaml
4. create-integration-pr.yaml

#### Build image

This `Build and push multi-arch images` github action workflow builds and pushes a multi-arch Docker image to [GHCR](https://github.com/alphagov/datagovuk/pkgs/container/datagovuk)

#### Create Integration PR

The `create-integration-pr.yaml` workflow runs after `build-image.yaml` completes on `main`. It then automatically opens a
pull request in [govuk-dgu-charts](https://github.com/alphagov/govuk-dgu-charts).

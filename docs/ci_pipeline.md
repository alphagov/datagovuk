# Our GitHub Actions Workflows

1. build-image.yaml
2. ci.yaml
3. create-integration-pr.yaml
4. trivy-scans.yaml

## On Pull request

When creating a pull request with base branch `main` or merging a change into the `main` branch.

It runs the CI workflow.

### CI Workflow

It runs these jobs:

- Linter tests
- CodeQl SAST security tests
- Django Python tests: Unit, Integration, E2E and coverage.

### On merge to main branch

It runs these workflows:

1. CI
2. trivy-scans.yaml
3. build-image.yaml
4. create-integration-pr.yaml

#### Trivy vulnerability scans

The trivy-scan workflow scans for cirtical or high risk vulnerabilities in our python uv dependencies. The PR fails if any are found. It, also, Dockerfile image vulnearabilities and secrets in the codebase.

#### Build image

This `Build and push multi-arch images` github action workflow builds docker images for each architecture listed in `build-config.yaml` and uploads them as untagged versions to [GHCR Untagged images](https://github.com/alphagov/datagovuk/pkgs/container/datagovuk/versions?filters%5Bversion_type%5D=untagged).

This workflow then combines those digests into a tagged manifest list and uploads them to [GHCR Tagged images](https://github.com/alphagov/datagovuk/pkgs/container/datagovuk/versions?filters%5Bversion_type%5D=tagged).

#### Create Integration PR

The create-integration-pr.yaml workflow waits for the build-image.yaml workflow to complete on the main branch (see workflow_run: ...).

Then using a github personal access token, this workflow creates a pull request in dgu-charts [see here](https://github.com/alphagov/govuk-dgu-charts/pull/777). The changes made are found in this script `./docker/create-pr.sh`, which updates the sha value `integration/datagovuk.yaml` in `govuk-dgu-charts`.

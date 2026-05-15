# Our GitHub Actions Workflows

1. build-image.yaml
2. ci.yaml
3. create-integration-pr.yaml
4. trivy-scans.yaml
5. create-pr-on-tags.yaml
6. build-image-on-tags.yaml
7. smoke-tests.yaml

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

### Build image

This `Build and push multi-arch images` github action workflow builds and pushes a multi-arch Docker image to [GHCR](https://github.com/alphagov/datagovuk/pkgs/container/datagovuk)

### Create Integration PR

The `create-integration-pr.yaml` workflow runs after `build-image.yaml` completes on `main`. It then automatically opens a
pull request in [govuk-dgu-charts](https://github.com/alphagov/govuk-dgu-charts).

## On tag creation (release to staging & production)

After a git tag/release is created, it runs these workflows:

1. build-image-on-tags.yaml
2. create-pr-on-tags.yaml

### Build image on tags

This `build-image-on-tags.yaml` workflow calls `build-image.yaml` and provides the input `buildType: build_push_with_gittag` building and pushing an image that's tagged with a git tag like `v1.2.3`.

### Create pull requests on tags

This `create-pr-on-tags.yaml` workflow is triggered when `build-image-on-tags.yaml` is complete. It automatically opens two PRs in [govuk-dgu-charts](https://github.com/alphagov/govuk-dgu-charts) for staging and production.

## On manual trigger

Uses workflow_dispatch github action to manually trigger the below workflows.

### Smoke tests

The `smoke-tests.yml` workflow runs sanity checks on integration (default) or a provided environment. This is for post deployment verification testing.

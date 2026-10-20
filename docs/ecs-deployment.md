# ECS Deployment to Integration

Interim documentation. This is a first step towards full CI/CD deployment management.

## Current State

This workflow is **manually dispatched only**. You trigger it manually and provide a git SHA. No automatic deploys.

The workflow copies the Docker image from GitHub Container Registry to the integration AWS account ECR, then updates the ECS task definition and deploys to the integration cluster with rolling restart.

Requires valid 40-character git SHA of an image already in GHCR.

## What This Does

1. Takes a Docker image SHA from GHCR (already built and in registry)
2. Copies image to integration account ECR
3. Registers new task definition with the image
4. Updates ECS service with rolling restart (new tasks replace old ones gradually)
5. Health checks happen before old tasks are stopped

## How To Use

Manual workflow dispatch in GitHub Actions. Provide the full git SHA of the image you want to deploy.

## Future Direction

In the near future, we will move to an ECR-only workflow. This means:
- Tagging and release process will be recreated
- Managing task definitions and tagged artifacts consistently across environments

This is a starting point focusing on integration. Once we have integration working well with smoke tests, we'll introduce staging and production in a deliberate fashion.

Eventually the goal is:
- Deployments to integration trigger smoke tests
- Full CI/CD pipeline manages task definitions and tagged artifacts
- Unified deployment strategy across integration, staging, and production

## Monitoring Deployment

Check AWS console under ECS cluster `integration`, service `datagovuk` to watch tasks being replaced.

Or tail logs in CloudWatch at `/ecs/integration/datagovuk`.

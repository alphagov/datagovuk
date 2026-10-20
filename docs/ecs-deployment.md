# ECS Deployment to Integration

Interim documentation. This is a first step towards full CI/CD deployment management.

## Current State

This workflow is **manually dispatched**. It does not automatically deploy on every push to main.

The workflow copies the Docker image from GitHub Container Registry to the integration AWS account ECR, then updates the ECS task definition and deploys to the integration cluster with rolling restart.

## What This Does

1. Takes a Docker image SHA from GHCR (already built and in registry)
2. Copies image to integration account ECR
3. Registers new task definition with the image
4. Updates ECS service with rolling restart (new tasks replace old ones gradually)
5. Health checks happen before old tasks are stopped

## How To Use

Manual workflow dispatch in GitHub Actions. Provide the full git SHA of the image you want to deploy.

## Next Steps

This is part of a series. Eventually:
- Deployments to integration will trigger smoke tests
- Full CI/CD pipeline will manage task definitions and tagged artifacts
- Deployment strategy across test, integration, staging, and production will be unified

For now this is a starting point and manual trigger only.

## Monitoring Deployment

Check AWS console under ECS cluster `integration`, service `datagovuk` to watch tasks being replaced.

Or tail logs in CloudWatch at `/ecs/integration/datagovuk`.

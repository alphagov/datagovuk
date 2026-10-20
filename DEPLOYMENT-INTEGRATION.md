# Automated Deployment to Integration

Django datagovuk now deploys automatically to the integration environment on every merge to main.

## Deployment Flow

When code is merged to `main`, the following happens automatically:

1. **Merge to main** triggers GitHub Actions
2. **CI checks** run (tests with 100% coverage, linting, security scans)
3. **Build image** - if all checks pass, Docker image is built for linux/arm64 and pushed to GitHub Container Registry (GHCR)
4. **Push to ECR** - image is copied from GHCR to AWS integration account ECR registry
5. **Deploy to ECS** - new task definition is registered and deployed to the integration cluster
6. **Rolling restart** - ECS replaces old tasks with new ones gradually. Each new task is health checked before old ones are terminated. This gives zero-downtime deployments.

## Deployment Configuration

**Trigger:** Push to `main` branch (excluding `docs/` changes)

**AWS Account:** gds-ndl-integration (836822603246)

**ECS Cluster:** integration

**ECS Service:** datagovuk

**ALB health check:** `/health/`

**Replicas:** 1 (configurable in infrastructure Terraform)

**Region:** eu-west-2

## Rolling Deployment Details

The deployment uses `wait-for-service-stability: true`, which means:
- New task starts running the new image
- ALB health check waits for it to return 200 OK on `/health/`
- Once healthy, the old task is stopped
- This repeats for each replica

With 1 replica, this means a few seconds of traffic going to either the old or new version, but never a hard restart. If we increase replicas, the rolling behavior becomes more gradual.

## Monitoring Deployment

### In AWS Console

Go to ECS cluster `integration` → service `datagovuk`:
- Watch task count change as old tasks stop and new ones start
- Check CloudWatch Logs at `/ecs/integration/datagovuk` to see app startup
- ALB target group shows task health status

### Via AWS CLI

```bash
aws-vault exec gds-ndl-integration-developer --no-session -- \
  aws ecs describe-services \
    --cluster integration \
    --services datagovuk \
    --region eu-west-2
```

### Via GitHub

Go to the repository Actions tab. The workflow that ran is called "Push to ECR and promote". You can see:
- What triggered the deployment (merge commit SHA)
- Build time
- Push to ECR time
- Deployment status

## Rollback

If something goes wrong after deployment:

1. Redeploy the previous commit:
   ```bash
   git revert HEAD
   git push
   ```
   This triggers a new deployment with the old code.

2. Or manually force the old task definition revision in AWS Console → ECS → Service → Deployments, though the automatic redeploy is cleaner.

## Failing Deployments

If CI fails (tests don't pass, linting issues, security scan fails):
- Build image step is skipped
- No image is pushed
- No deployment happens

Fix the failing checks and push again. The workflow will retry automatically.

## Secrets and Authentication

- Docker image push uses GitHub Container Registry token (automatic)
- AWS authentication uses OIDC token exchange via GitHub Actions
- No credentials are stored in the repository
- Integration account has an OIDC trust relationship configured for this repository

These are managed in datagovuk-infrastructure Terraform (github_oidc module).

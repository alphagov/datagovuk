#!/bin/bash

set -eux

if [[ ${IS_TAG:-} = "true" ]]; then
  export IMAGE_TAG="${GH_REF}"
  export SOURCE_BRANCH="main"
else
  export IMAGE_TAG=$(gh api repos/alphagov/datagovuk/branches/${GH_REF} | jq .commit.sha -r)
  export SOURCE_BRANCH=${GH_REF}
fi

git config --global user.email "govuk-ci@users.noreply.github.com"
git config --global user.name "govuk-ci"

gh auth setup-git
git clone https://github.com/alphagov/govuk-dgu-charts.git charts

cd charts/charts/datagovuk/images

for ENV in $(echo $ENVS | tr "," " "); do
  (
    cd "${ENV}"
    yq -i '.tag = env(IMAGE_TAG)' "datagovuk.yaml"
    yq -i '.branch = env(SOURCE_BRANCH)' "datagovuk.yaml"
    git add "datagovuk.yaml"

    if git diff --cached --quiet -- "datagovuk.yaml"; then
      echo "Nothing to commit"
    else
      BRANCH="ci/${IMAGE_TAG}-${ENV}"
      # Check remote (not local) — git show-ref only sees local refs in a fresh clone
      if git ls-remote --exit-code --heads origin "${BRANCH}" >/dev/null 2>&1; then
        echo "Branch ${BRANCH} already exists on govuk-dgu-charts — skipping"
      else
        git checkout -b ${BRANCH}
        git commit -m "Update datagovuk image tags for ${ENV} to ${IMAGE_TAG}"
        git push --set-upstream origin "${BRANCH}"
        gh pr create --title "Update datagovuk image tags for ${ENV} (${IMAGE_TAG})" --base main --head "${BRANCH}" --fill --repo alphagov/govuk-dgu-charts
      fi
    fi
  )
done

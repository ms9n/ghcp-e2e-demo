#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-ghcpe2e-rg}"
BASE_NAME="${BASE_NAME:-ghcpe2e}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
GITHUB_REPO_VAR="${GITHUB_REPO:-}"
COPILOT_TOKEN="${COPILOT_GITHUB_TOKEN:-}"
GH_TOKEN="${GITHUB_TOKEN:-}"

echo "==> Fetching ACR details..."
ACR_NAME=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.acrName.value' -o tsv)
ACR_LOGIN_SERVER=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.acrLoginServer.value' -o tsv)

IMAGE_NAME="${ACR_LOGIN_SERVER}/ghcp-e2e-demo:${IMAGE_TAG}"

echo "==> Logging in to ACR: $ACR_NAME"
az acr login --name "$ACR_NAME"

echo "==> Building Docker image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

echo "==> Pushing image to ACR..."
docker push "$IMAGE_NAME"

echo "==> Deploying to Container App..."
LOCATION=$(az group show --name "$RESOURCE_GROUP" --query location -o tsv)

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file infra/main.bicep \
  --parameters \
    baseName="$BASE_NAME" \
    location="$LOCATION" \
    containerImage="$IMAGE_NAME" \
    copilotGithubToken="$COPILOT_TOKEN" \
    githubToken="$GH_TOKEN" \
    githubRepo="$GITHUB_REPO_VAR" \
  --output table

APP_FQDN=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.containerAppFqdn.value' -o tsv)

echo ""
echo "==> Deployment complete!"
echo "    App URL: https://$APP_FQDN"
echo "    Trigger error: https://$APP_FQDN/calculate?a=10&b=0"

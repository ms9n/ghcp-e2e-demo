#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-ghcpe2e-rg}"
LOCATION="${LOCATION:-eastus}"
BASE_NAME="${BASE_NAME:-ghcpe2e}"

echo "==> Creating resource group: $RESOURCE_GROUP in $LOCATION"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output table

echo "==> Deploying infrastructure via Bicep (without container image)..."
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file infra/main.bicep \
  --parameters baseName="$BASE_NAME" location="$LOCATION" \
  --output table

ACR_NAME=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.acrName.value' -o tsv)

echo ""
echo "==> Infrastructure provisioned successfully!"
echo "    Resource Group : $RESOURCE_GROUP"
echo "    ACR Name       : $ACR_NAME"
echo ""
echo "Next step: run scripts/deploy-app.sh to build and deploy the app."

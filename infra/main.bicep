@description('Location for all resources')
param location string = resourceGroup().location

@description('Base name for all resources')
param baseName string = 'ghcpe2e'

@description('Container image to deploy (e.g. myacr.azurecr.io/ghcp-e2e-demo:latest)')
param containerImage string = ''

@secure()
@description('PAT with Copilot Requests permission')
param copilotGithubToken string = ''

@secure()
@description('PAT with repo/issues scope')
param githubToken string = ''

@description('GitHub repo in owner/repo format')
param githubRepo string = ''

var acrName = '${baseName}acr${uniqueString(resourceGroup().id)}'
var lawName = '${baseName}-law'
var envName = '${baseName}-env'
var appName = '${baseName}-app'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: true }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: lawName
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: envName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = if (!empty(containerImage)) {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
      }
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        { name: 'acr-password', value: acr.listCredentials().passwords[0].value }
        { name: 'copilot-github-token', value: copilotGithubToken }
        { name: 'github-token', value: githubToken }
      ]
    }
    template: {
      containers: [
        {
          name: appName
          image: containerImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'COPILOT_GITHUB_TOKEN', secretRef: 'copilot-github-token' }
            { name: 'GITHUB_TOKEN', secretRef: 'github-token' }
            { name: 'GITHUB_REPO', value: githubRepo }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
}

output acrLoginServer string = acr.properties.loginServer
output acrName string = acr.name
output containerAppEnvName string = containerAppEnv.name
output containerAppName string = appName
output containerAppFqdn string = (!empty(containerImage)) ? containerApp.properties.configuration.ingress.fqdn : ''

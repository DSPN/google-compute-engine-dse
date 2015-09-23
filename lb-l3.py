import yaml


def GenerateConfig(context):
  prefix = context.env['name']

  hcName = prefix + '-hc'
  tpName = prefix + '-tp'
  frName = prefix + '-fr'

  port = context.properties['port']
  region = context.properties['region']

  resources = [{
      'name': hcName,
      'type': 'compute.v1.httpHealthCheck',
      'properties': {
          'port': port,
          'requestPath': '/_ah/health'
      }
  }, {
      'name': tpName,
      'type': 'compute.v1.targetPool',
      'properties': {
          'region': region,
          'healthChecks': ['$(ref.' + hcName + '.selfLink)']
      }
  }, {
      'name': frName,
      'type': 'compute.v1.forwardingRule',
      'properties': {
          'region': region,
          'portRange': port,
          'target': '$(ref.' + tpName + '.selfLink)'
      }
  }]

  return yaml.dump({'resources': resources})

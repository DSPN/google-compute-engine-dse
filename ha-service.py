import yaml

def GenerateConfig(context):
  lbName = context.env['deployment'] + '-lb'
  region = context.properties['zones'][0][:-2]

  port = context.properties['port']
  minSize = context.properties['minSize']
  maxSize = context.properties['maxSize']

  # YAML config.
  config = {'resources' : []}

  # A zonal service.py resource for each zone in the properties list.
  for zone in context.properties['zones']:
    service = {
      'name': context.env['deployment'] + '-service-' + zone,
      'type': 'service.py',
      'properties': {
        'image': context.properties['image'],
        'port': port,
        'targetPool': lbName + '-tp',
        'minSize': minSize,
        'maxSize': maxSize,
        'zone': zone
      }
    }

    config['resources'].append(service)

  # A L3 load balancer setup for the HA service.
  lb = {
    'name': lbName,
    'type': 'lb-l3.py',
    'properties': {
      'port': port,
      'region': region
    }
  }

  config['resources'].append(lb)

  return yaml.dump(config)


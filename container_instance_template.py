"""Creates a Container VM with the provided Container manifest."""

from container_helper import GenerateManifest
import yaml


def GenerateConfig(context):
  image = ''.join(['https://www.googleapis.com/compute/v1/',
                  'projects/google-containers/global/images/',
                  context.properties['containerImage']])
  defaultNetwork = ''.join(['https://www.googleapis.com/compute/v1/projects/',
                           context.env['project'],
                           '/global/networks/default'])

  instanceTemplate = {
      'name': context.env['name'],
      'type': 'compute.v1.instanceTemplate',
      'properties': {
          'properties': {
              'metadata': {
                  'items': [{
                      'key': 'google-container-manifest',
                      'value': GenerateManifest(context)
                      }]
                  },
              'machineType': 'f1-micro',
              'disks': [{
                  'deviceName': 'boot',
                  'boot': True,
                  'autoDelete': True,
                  'mode': 'READ_WRITE',
                  'type': 'PERSISTENT',
                  'initializeParams': { 'sourceImage': image }
                  }],
              'networkInterfaces': [{
                  'accessConfigs': [{
                      'name': 'external-nat',
                      'type': 'ONE_TO_ONE_NAT'
                      }],
                  'network': defaultNetwork
                  }]
              }
          }
      }

  return yaml.dump({'resources': [instanceTemplate]})


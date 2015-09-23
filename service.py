"""Creates autoscaled, network LB IGM running specified docker image."""

import yaml

# Defaults
size = 0

MIN_SIZE_KEY = 'minSize'
DEFAULT_MIN_SIZE = 1

MAX_SIZE_KEY = 'maxSize'
DEFAULT_MAX_SIZE = 1

CONTAINER_IMAGE_KEY = 'containerImage'
DEFAULT_CONTAINER_IMAGE = 'centos-7'

DOCKER_ENV_KEY = 'dockerEnv'
DEFAULT_DOCKER_ENV = {}


def GenerateConfig(context):
  """Generate YAML resource configuration."""

  # Set up some defaults if the user didn't provide any
  if MIN_SIZE_KEY not in context.properties:
    context.properties[MIN_SIZE_KEY] = DEFAULT_MIN_SIZE
  if MAX_SIZE_KEY not in context.properties:
    context.properties[MAX_SIZE_KEY] = DEFAULT_MAX_SIZE
  if CONTAINER_IMAGE_KEY not in context.properties:
    context.properties[CONTAINER_IMAGE_KEY] = DEFAULT_CONTAINER_IMAGE
  if DOCKER_ENV_KEY not in context.properties:
    context.properties[DOCKER_ENV_KEY] = DEFAULT_DOCKER_ENV

  name = context.env['name']
  port = context.properties['port']
  targetPool = context.properties['targetPool']
  zone = context.properties['zone']

  igmName = name + '-igm'
  itName = name + '-it'

  resources = [{
      'name': itName,
      'type': 'container_instance_template.py',
      'properties': {
          CONTAINER_IMAGE_KEY: context.properties[CONTAINER_IMAGE_KEY],
          DOCKER_ENV_KEY: context.properties[DOCKER_ENV_KEY],
          'dockerImage': context.properties['image'],
          'port': port
      }
  }, {
      'name': igmName,
      'type': 'replicapool.v1beta2.instanceGroupManager',
      'properties': {
          'baseInstanceName': name + '-instance',
          'instanceTemplate': '$(ref.' + itName + '.selfLink)',
          'size': size,
          'targetPools': ['$(ref.' + targetPool + '.selfLink)'],
          'zone': zone
      }
  }, {
      'name': name + '-as',
      'type': 'autoscaler.v1beta2.autoscaler',
      'properties': {
          'autoscalingPolicy': {
              'minNumReplicas': context.properties[MIN_SIZE_KEY],
              'maxNumReplicas': context.properties[MAX_SIZE_KEY]
          },
          'target': '$(ref.' + igmName + '.selfLink)',
          'zone': zone
      }
  }]

  return yaml.dump({'resources': resources})


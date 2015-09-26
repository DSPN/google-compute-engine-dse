import yaml
import copy

def GenerateConfig(context):

  # YAML config.
  config = {'resources' : []}

  # A zonal vm_multiple_instances resource for each zone in the properties list.
  for zone in context.properties['zones']:
    newproperties = copy.deepcopy(context.properties)
    newproperties["zone"] = zone   
    service = {
      'name': context.env['deployment'] + '-service-' + zone,
      'type': 'vm_multiple_instances.py',
      'properties': newproperties
    }
    
    config['resources'].append(service)

  return yaml.dump(config)

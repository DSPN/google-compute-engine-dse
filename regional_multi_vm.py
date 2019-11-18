import yaml
import copy


def GenerateConfig(context):
    config = {'resources': []}

    # A zonal vm_multiple_instances resource for each zone in the properties list.
    index = 0
    for zone in context.properties['zones']:
        new_properties = copy.deepcopy(context.properties)
        new_properties['zone'] = zone
        new_properties['network'] = context.properties['network']
        new_properties['subnetwork'] = context.properties['subnetworks'][index]
        index += 1
        service = {
            'name': context.env['deployment'] + '-' + zone,
            'type': 'vm_multiple_instances.py',
            'properties': new_properties
        }

        config['resources'].append(service)

    return yaml.dump(config)

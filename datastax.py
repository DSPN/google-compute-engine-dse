import yaml
import base64
import json


def GenerateFirewall(context):
    name = 'opscenterfirewall-' + context.env['name']
    firewalls = [
        {
            'name': name,
            'type': 'compute.v1.firewall',
            'properties': {
                'sourceRanges': [
                    '0.0.0.0/0'
                ],
                'allowed': [{
                    'IPProtocol': 'tcp',
                    'ports': ['8888', '8443']
                }]
            }
        }
    ]

    return firewalls


def GenerateReferencesList(context):
    reference_list = []
    n_of_copies = context.properties['nodesPerZone']
    dep_name = context.env['deployment']
    for zone in context.properties['zones']:
        for idx in range(1, n_of_copies + 1):
            node_name = '$(ref.' + dep_name + '-service-' + zone + '-' + str(idx) + '-vm' + '.selfLink)'
            reference_list.append(node_name)
    return ' '.join(reference_list)


def GenerateConfig(context):
    config = {'resources': []}

    #seed_nodes_dns_names = ''
    #for zone in context.properties['zones']:
    #    seed_nodes_dns_names += context.env['deployment'] + '-service-' + zone + '-1-vm,'
    #seed_nodes_dns_names = seed_nodes_dns_names[:-1]

    # just going to do one seed for now
    seed_nodes_dns_names = context.env['deployment'] + '-service-' + context.properties['zones'][0] + '-1-vm'

    dse_node_script = '''
        #!/usr/bin/env bash

        wget https://github.com/DSPN/install-datastax/archive/master.zip
        apt-get -y install unzip
        unzip master.zip
        cd install-datastax-master/bin

        cloud_type="google"
        zone=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/zone" | grep -o [[:alnum:]-]*$)
        data_center_name=$zone
        seed_nodes_dns_names=''' + seed_nodes_dns_names + '''
        echo "Configuring nodes with the settings:"
        echo cloud_type \'$cloud_type\'
        echo data_center_name \'$data_center_name\'
        echo seed_nodes_dns_names \'$seed_nodes_dns_names\'
        ./dse.sh $cloud_type $data_center_name $seed_nodes_dns_names
        '''

    zonal_clusters = {
        'name': 'clusters-' + context.env['name'],
        'type': 'regional_multi_vm.py',
        'properties': {
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1504-vivid-v20160114a',
            'zones': context.properties['zones'],
            'machineType': context.properties['machineType'],
            'network': 'default',
            'numberOfVMReplicas': context.properties['nodesPerZone'],
            'disks': [
                {
                    'deviceName': 'vm-test-data-disk',
                    'type': 'PERSISTENT',
                    'boot': 'false',
                    'autoDelete': 'true',
                    'initializeParams': {
                        'diskType': 'pd-ssd',
                        'diskSizeGb': context.properties['diskSize']
                    }
                }
            ],
            'bootDiskType': 'pd-standard',
            'metadata': {
                'items': [
                    {
                        'key': 'startup-script',
                        'value': dse_node_script
                    }
                ]
            }
        }
    }

    ops_center_script = '''
      #!/usr/bin/env bash

      wget https://github.com/DSPN/install-datastax/archive/master.zip
      apt-get -y install unzip
      unzip master.zip
      cd install-datastax-master/bin

      seed_nodes_dns_names=''' + seed_nodes_dns_names + '''
      ./opscenter.sh $seed_nodes_dns_names
    '''

    ops_center_node = {
        'name': 'opscenter-' + context.env['name'],
        'type': 'vm_instance.py',
        'properties': {
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1504-vivid-v20160114a',
            'zone': context.properties['opsCenterZone'],
            'machineType': context.properties['machineType'],
            'network': 'default',
            'bootDiskType': 'pd-standard',
            'serviceAccounts': [{
                'email': 'default',
                'scopes': ['https://www.googleapis.com/auth/compute']
            }],
            'metadata': {
                'items': [
                    {
                        'key': 'startup-script',
                        'value': ops_center_script
                    },
                    {
                        'key': 'bogus-references',
                        'value': GenerateReferencesList(context)
                    }
                ]
            }
        }
    }

    config['resources'].append(zonal_clusters)
    config['resources'].append(ops_center_node)
    config['resources'].extend(GenerateFirewall(context))

    return yaml.dump(config)

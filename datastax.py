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
                        'value': '''
                          #!/usr/bin/env bash
                          cloud_type="google"
                          data_center_name="foo"

                          location=$2 #this is the location of the seed and OpsCenter, not necessarily of this node
                          uniqueString=$3
                          seed_node_dns_name="dc0vm0$uniqueString.$location.cloudapp.azure.com"
                          seed_node_public_ip=`dig +short $seed_node_dns_name | awk '{ print ; exit }'`

                          wget https://github.com/DSPN/install-datastax/archive/master.zip
                          apt-get -y install unzip
                          unzip master.zip
                          cd install-datastax-master/bin

                          ./dse.sh $cloud_type $data_center_name $seed_node_public_ip
                          '''
                    }
                ]
            }
        }
    }

    ops_center_script = '''
      #!/usr/bin/env bash

      location=$1
      uniqueString=$2

      seed_node_dns_name="dc0vm0$uniqueString.$location.cloudapp.azure.com"
      seed_node_public_ip=`dig +short $seed_node_dns_name | awk '{ print ; exit }'`

      wget https://github.com/DSPN/install-datastax/archive/master.zip
      apt-get -y install unzip
      unzip master.zip
      cd install-datastax-master/bin

      #./opscenter.sh $seed_node_public_ip
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

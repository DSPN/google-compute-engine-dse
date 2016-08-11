import yaml

import common
import default

def GenerateFirewall(context):
    name = context.env['deployment'] + '-opscenter-firewall'
    firewalls = [
        {
            'name': name,
            'type': 'compute.v1.firewall',
            'properties': {
                'network': common.MakeGlobalComputeLink(context, default.NETWORK),
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


def GetZonesList(context):
    zones = []
    if context.properties['usEast1b']:
        zones.append('us-east1-b')
    if context.properties['usEast1c']:
        zones.append('us-east1-c')
    if context.properties['usEast1d']:
        zones.append('us-east1-d')
    if context.properties['usCentral1a']:
        zones.append('us-central1-a')
    if context.properties['usCentral1b']:
        zones.append('us-central1-b')
    if context.properties['usCentral1c']:
        zones.append('us-central1-c')
    if context.properties['usCentral1f']:
        zones.append('us-central1-f')
    if context.properties['europeWest1b']:
        zones.append('europe-west1-b')
    if context.properties['europeWest1c']:
        zones.append('europe-west1-c')
    if context.properties['europeWest1d']:
        zones.append('europe-west1-d')
    if context.properties['asiaEast1a']:
        zones.append('asia-east1-a')
    if context.properties['asiaEast1b']:
        zones.append('asia-east1-b')
    if context.properties['asiaEast1c']:
        zones.append('asia-east1-c')
    assert len(zones) > 0, 'No zones selected for DataStax Enterprise nodes'
    return zones


def GenerateConfig(context):
    config = {'resources': []}

    # Set zones list based on zone booleans.
    if ('zones' not in context.properties or len(context.properties['zones']) == 0):
      context.properties['zones'] = GetZonesList(context)

    # Set zone property to match ops center zone. Needed for calls to common.MakeGlobalComputeLink.
    context.properties['zone'] = context.properties['opsCenterZone']

    seed_nodes_dns_names = context.env['deployment'] + '-' + context.properties['zones'][0] + '-1-vm.c.' + context.env['project'] + '.internal'
    opscenter_node_name = context.env['deployment'] + '-opscenter-vm'
    opscenter_dns_name = opscenter_node_name + '.c.' + context.env['project'] + '.internal'

    dse_node_script = '''
        #!/usr/bin/env bash

        mkdir /mnt
        /usr/share/google/safe_format_and_mount -m "mkfs.ext4 -F" /dev/disk/by-id/google-${HOSTNAME}-data-disk /mnt

        apt-get -y install unzip

        wget https://github.com/DSPN/install-datastax-ubuntu/archive/5.0.1-2.zip
        unzip 5.0.1-2.zip
        cd install-datastax-ubuntu-5.0.1-2/bin

        cloud_type="gce"
        seed_nodes_dns_names=''' + seed_nodes_dns_names + '''

        zone=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/zone" | grep -o [[:alnum:]-]*$)
        data_center_name=$zone
        opscenter_dns_name=''' + opscenter_dns_name + '''

        echo "Configuring nodes with the settings:"
        echo cloud_type $cloud_type
        echo seed_nodes_dns_names $seed_nodes_dns_names
        echo data_center_name $data_center_name
        echo opscenter_dns_name $opscenter_dns_name

        ./dse.sh $cloud_type $seed_nodes_dns_names $data_center_name $opscenter_dns_name
        '''

    zonal_clusters = {
        'name': 'clusters-' + context.env['name'],
        'type': 'regional_multi_vm.py',
        'properties': {
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/datastax-public/global/images/datastax-ubuntu1404-img-03172016',
            'zones': context.properties['zones'],
            'machineType': context.properties['machineType'],
            'network': context.properties['network'],
            'numberOfVMReplicas': context.properties['nodesPerZone'],
            'disks': [
                {
                    'deviceName': 'vm-data-disk',
                    'type': 'PERSISTENT',
                    'boot': 'false',
                    'autoDelete': 'true',
                    'initializeParams': {
                        'diskType': context.properties['dataDiskType'],
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

    opscenter_script = '''
      #!/usr/bin/env bash

      apt-get -y install unzip

      wget https://github.com/DSPN/install-datastax-ubuntu/archive/5.0.1-2.zip
      unzip 5.0.1-2.zip
      cd install-datastax-ubuntu-5.0.1-2/bin

      cloud_type="gce"
      seed_nodes_dns_names=''' + seed_nodes_dns_names + '''
      echo "Configuring nodes with the settings:"
      echo cloud_type $cloud_type
      echo seed_nodes_dns_names $seed_nodes_dns_names
      ./opscenter.sh $cloud_type $seed_nodes_dns_names
    '''

    opscenter_node_name = context.env['deployment'] + '-opscenter-vm'
    opscenter_node = {
        'name': opscenter_node_name,
        'type': 'vm_instance.py',
        'properties': {
            'instanceName': opscenter_node_name,
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/datastax-public/global/images/datastax-ubuntu1404-img-03172016',
            'zone': context.properties['opsCenterZone'],
            'machineType': context.properties['machineType'],
            'network': context.properties['network'],
            'bootDiskType': 'pd-standard',
            'serviceAccounts': [{
                'email': 'default',
                'scopes': ['https://www.googleapis.com/auth/compute']
            }],
            'metadata': {
                'items': [
                    {
                        'key': 'startup-script',
                        'value': opscenter_script
                    }
                ]
            }
        }
    }

    config['resources'].append(zonal_clusters)
    config['resources'].append(opscenter_node)
    config['resources'].extend(GenerateFirewall(context))

    first_enterprise_node_name = context.env['deployment'] + '-' + context.properties['zones'][0] + '-1-vm'
    outputs = [
        {
            'name': 'project',
            'value': context.env['project']
        },
        {
            'name': 'opsCenterNodeName',
            'value': opscenter_node_name
        },
        {
            'name': 'firstEnterpriseNodeName',
            'value': first_enterprise_node_name
        },
        {
            'name': 'firstEnterpriseNodeSelfLink',
            'value': '$(ref.' + first_enterprise_node_name + '.selfLink)'
        },
        {
            'name': 'zoneList',
            'value': ', '.join(context.properties['zones'])
        },
        {
            'name': 'x-status-type',
            'value': 'console'
        },
        {
            'name': 'x-status-instance',
            'value': opscenter_node_name
        }
    ]
    config['outputs'] = outputs

    return yaml.dump(config)

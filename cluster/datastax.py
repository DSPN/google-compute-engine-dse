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
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1504-vivid-v20151120',
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
                          #!/bin/bash
                          mkdir /mnt
                          /usr/share/google/safe_format_and_mount -m "mkfs.ext4 -F" /dev/disk/by-id/google-${HOSTNAME}-test-data-disk /mnt
                          chmod 777 /mnt
                          apt-get update
                          apt-get install openjdk-7-jdk -yqq
                          '''
                    }
                ]
            }
        }
    }

    ops_center_script = '''
    #! /bin/bash
    ssh-keygen -b 2048 -t rsa -f /tmp/sshkey -q -N ""
    echo -n 'root:' | cat - /tmp/sshkey.pub > temp && mv temp /tmp/sshkey.pub
    gcloud compute project-info add-metadata --metadata-from-file sshKeys=/tmp/sshkey.pub
    apt-get update
    apt-get install openjdk-7-jdk -yqq

    echo "Installing OpsCenter"
    echo "deb http://debian.datastax.com/community stable main" | tee -a /etc/apt/sources.list.d/datastax.community.list
    curl -L http://debian.datastax.com/debian/repo_key | apt-key add -
    apt-get update
    apt-get -y install opscenter=5.2.2

    echo "Starting OpsCenter"
    sudo service opscenterd start

    echo "Waiting for OpsCenter to start..."
    sleep 15

    echo "Waiting for Java to install on the nodes..."
    sleep 120

    wget https://raw.githubusercontent.com/DSPN/google-cloud-platform-dse/master/cluster/provision/opsCenter.py

    echo "Generating a provision.json file"
    python opsCenter.py '''

    # parameters go here
    ops_center_script += context.env['deployment'] + ' '
    ops_center_script += base64.b64encode(json.dumps(context.properties['zones'])) + ' '
    ops_center_script += str(context.properties['nodesPerZone']) + ' '
    ops_center_script += str(context.properties['nodeType'])

    ops_center_script += '''
    echo "Provisioning a new cluster using provision.json"
    curl --insecure -H "Accept: application/json" -X POST http://127.0.0.1:8888/provision -d @provision.json
    '''

    ops_center_node = {
        'name': 'opscenter-' + context.env['name'],
        'type': 'vm_instance.py',
        'properties': {
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1504-vivid-v20151120',
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

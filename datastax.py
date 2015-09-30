import yaml


def GenerateFirewall(context):
    """Generates a firewall"""
    name = 'opscenterfirewall-' + context.env['name']
    prop = context.properties
    firewalls = []
    # pyformat: disable
    firewalls.append({
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
    })
    # pyformat: enable
    return firewalls


def GenerateConfig(context):
    # YAML config.
    config = {'resources': []}

    zonal_clusters = {
        'name': 'clusters-' + context.env['name'],
        'type': 'regional_multi_vm.py',
        'properties': {
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1410-utopic-v20150625',
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
                        'value': '''|
                            #!/bin/bash
                            mkdir -p /mnt/data
                            chmod 777 /mnt/data
                            /usr/share/google/safe_format_and_mount -m "mkfs.ext4 -F" /dev/disk/by-id/google-${HOSTNAME}-test-data-disk /mnt/data
                            apt-get update
                            apt-get install openjdk-7-jdk -yqq
                            '''
                    }
                ]
            }
        }
    }

    ops_center_node = {
        'name': 'opscenter-' + context.env['name'],
        'type': 'vm_instance.py',
        'properties': {
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1410-utopic-v20150625',
            'zone': context.properties['opsCenterZone'],
            'machineType': context.properties['machineType'],
            'network': 'default',
            'bootDiskType': 'pd-standard',
            'metadata': {
                'items': [
                    {
                        'key': 'startup-script',
                        'value': '''|
                            #! /bin/bash
                            apt-get update
                            apt-get install openjdk-7-jdk -yqq

                            echo "Installing OpsCenter"
                            echo "deb http://debian.datastax.com/community stable main" | tee -a /etc/apt/sources.list.d/datastax.community.list
                            curl -L http://debian.datastax.com/debian/repo_key | apt-key add -
                            apt-get -y install opscenter=5.2.1

                            echo "Starting OpsCenter"
                            sudo service opscenterd start

                            echo "Waiting for OpsCenter to start..."
                            sleep 15
                            '''
                    }
                ]
            }
        }
    }

    config['resources'].append(zonal_clusters)
    config['resources'].append(ops_center_node)
    config['resources'].extend(GenerateFirewall(context))

    return yaml.dump(config)

import yaml
import random
import string

URL_BASE = 'https://www.googleapis.com/compute/v1/projects/'

def GenerateConfig(context):
    config = {'resources': []}

    # Set deployment
    deployment = context.env['deployment']

    # Set serviceAccount
    serviceAccountEmail = context.env['project_number'] + '-compute@developer.gserviceaccount.com'

    # Set region, network, subnet
    region = context.properties['region']
    network = URL_BASE + context.env['project'] + '/global/networks/'+ context.properties['network']
    subnet = URL_BASE + context.env['project'] + '/regions/' + region + '/subnetworks/' +  context.properties['subnet']

    # Set OpsCenter variables
    opscenter_zone = context.properties['opscZone']
    opsc_admin_pwd = context.properties['opsCenterAdminPwd']
    opscenter_node_name = deployment + '-opscenter-vm'
    opscenter_dns_name = opscenter_node_name + '.c.' + context.env['project'] + '.internal.'
    opscenter_machine_type = ''.join([URL_BASE,
      context.env['project'], '/zones/',
      opscenter_zone, '/machineTypes/',
      context.properties['opscMachineType']])
    opscenter_vm_disk_type = ''.join([URL_BASE,
      context.env['project'], '/zones/',
      opscenter_zone, '/diskTypes/pd-standard'])

    # Generate a random bucket name
    bucket_suffix = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in xrange(10)])
    sshkey_bucket = deployment + '-ssh-pub-key-bucket-' + bucket_suffix

    # DSE version
    dse_version = context.properties['dseVersion']

    # Set cassandra's user password
    db_pwd = context.properties['cassandraPwd']

    # Set DataStax Academy credentials
    dsa_username = context.properties['dsa_username']
    dsa_password = context.properties['dsa_password']

    # Set cluster's name & size
    cluster_name = context.properties['clusterName']
    cluster_size = context.properties['clusterSize']

    # dse resources
    dse_node_it_resource = deployment + '-dse-node-it'
    dse_node_igm_resource = deployment + '-dse-node-igm'

    # Prepare a storage bucket to store our randomly generated SSH key pair for LCM's DSE install
    ssh_pub_key_bucket = {
        'name': sshkey_bucket,
        'type': 'storage.v1.bucket',
        'properties': {
            'name': sshkey_bucket,
        }
    }    
    config['resources'].append(ssh_pub_key_bucket)

    # Script to run inside a DSE node during instance instantiation
    dse_node_script = '''
        #!/usr/bin/env bash

	# If dse already installed, do nothing
        dpkg -s dse &> /dev/null
        retVal=$?
        if [ $retVal -eq 0 ]; then
          exit 0
        fi

        # Prepare for fresh DSE installation
        mkdir /mnt
        mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/google-vm-data-disk
        mount -o discard,defaults /dev/disk/by-id/google-vm-data-disk /mnt
        echo "/dev/disk/by-id/google-vm-data-disk /mnt ext4 discard,defaults 0 2" | tee -a /etc/fstab
        mkdir -p /mnt/data1
        mkdir -p /mnt/data1/data
        mkdir -p /mnt/data1/saved_caches
        mkdir -p /mnt/data1/commitlog
        mkdir -p /mnt/data1/dsefs
        chmod -R 777 /mnt/data1

        ##### Install DSE the LCM way
        cd ~ubuntu
        release="master"
        gsutil cp gs://dse-gcp-marketplace/dse-gcp-install-$release.tar.gz .
        tar -xvf dse-gcp-install-$release.tar.gz
        # install extra OS packages
        pushd dse-gcp-install-$release
        ./extra_packages.sh
        ./install_java.sh -o
        popd

        public_ip=`curl --retry 10 icanhazip.com`
        private_ip=`echo $(hostname -I)`
        node_id=$private_ip
        cluster_name=''' + cluster_name + '''
        rack="rack1"
        db_pwd=''' + db_pwd + '''

        zone=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/zone" | grep -o [[:alnum:]-]*$)
        data_center_name=$zone

        # Retrieve internal OPSC IP address
        opscenter_dns_name=''' + opscenter_dns_name + '''
        opsc_ip=`dig +short $opscenter_dns_name`

        # Grab lcm_pem.pub pubilc key from Google Cloud Storage
        cd ~ubuntu/.ssh/
        sshkey_bucket=''' + sshkey_bucket + '''
        gsutil cp gs://$sshkey_bucket/lcm_pem.pub .
        while [ $? -ne 0 ]
        do
            sleep 1s
            gsutil cp gs://$sshkey_bucket/lcm_pem.pub . 
        done
        chown ubuntu:ubuntu lcm_pem.pub
        cat lcm_pem.pub >> authorized_keys

        pushd ~ubuntu/dse-gcp-install-$release
        opsc_admin_pwd=''' + opsc_admin_pwd + '''

        ./addNode.py \
        --opscpw $opsc_admin_pwd \
        --opsc-ip $opsc_ip \
        --clustername $cluster_name \
        --dcname $data_center_name \
        --rack $rack \
        --pubip $private_ip \
        --privip $private_ip \
        --nodeid $node_id \

        popd
        '''

    dse_node_it = {
        # Create the Instance Template
        'name': dse_node_it_resource,
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'tags': {
                    'items': [
                       deployment,'dse-node'
                    ]
                },
                'machineType':
                    context.properties['machineType'],
                'networkInterfaces': [{
                    'network': network,
                    'subnetwork': subnet,
                    'accessConfigs': [{
                        'name': 'External NAT',
                        'type': 'ONE_TO_ONE_NAT'
                    }]
                }],
                'disks': [{
                    'deviceName': 'boot-disk',
                    'type': 'PERSISTENT',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage':
                          URL_BASE + 'datastax-public/global/images/datastax-enterprise-ubuntu-1604-xenial-v20180824'
                    }
                  },
                  {
                    'deviceName': 'vm-data-disk',
                    'type': 'PERSISTENT',
                    'boot': False,
                    'autoDelete': True,
                    'initializeParams': {
                        'diskType': context.properties['dataDiskType'],
                        'diskSizeGb': context.properties['dataDiskSize']
                    }
                  }
                ],
                'serviceAccounts': [{
                   'email': serviceAccountEmail,
                   'scopes': ['https://www.googleapis.com/auth/compute', 'https://www.googleapis.com/auth/cloudruntimeconfig', 'https://www.googleapis.com/auth/devstorage.full_control', 'https://www.googleapis.com/auth/cloud-platform']
                }],
                'metadata': {
                    'dependsOn': [
                        sshkey_bucket,
                    ],
                    'items': [ {
                        'key': 'startup-script',
                        'value': dse_node_script
                    }]
                }
            }
        }
    } 
    config['resources'].append(dse_node_it)

    dse_node_igm = {
        # Instance Group Manager
        'name': dse_node_igm_resource,
        'type': 'compute.v1.regionInstanceGroupManager',
        'properties': {
            'region': region,
            'baseInstanceName': deployment + '-dse-node',
            'instanceTemplate': '$(ref.%s.selfLink)' % dse_node_it_resource,
            'targetSize': context.properties['clusterSize']
        },
        'metadata': {
            'dependsOn': [
                  dse_node_it_resource,
            ]
        }
    }
    config['resources'].append(dse_node_igm)

    opscenter_script = '''
      #!/usr/bin/env bash

      # If opscenter already installed, do nothing
      dpkg -s opscenter &> /dev/null
      retVal=$?
      if [ $retVal -eq 0 ]; then
        exit 0
      fi
 
      # Prepare for fresh OpsCenter installation
      cd ~ubuntu
      release="master"
      gsutil cp gs://dse-gcp-marketplace/dse-gcp-install-$release.tar.gz .
      tar -xvf dse-gcp-install-$release.tar.gz

      # install extra OS packages, Java, and OpsCenter
      pushd dse-gcp-install-$release
      ./extra_packages.sh
      ./install_java.sh -o
      ./installOpsc.sh

      # Update password for default DSE OpsCenter administrator (admin)
      opsc_admin_pwd=''' + opsc_admin_pwd + '''
      ./set_opsc_pw_https.sh $opsc_admin_pwd
      popd

      # Generate lcm_pem private and pubilc keys
      pushd ~ubuntu/.ssh/
      ssh-keygen -t rsa -N '' -f lcm_pem
      chown ubuntu:ubuntu lcm_pem*
      privkey=$(readlink -f ~ubuntu/.ssh/lcm_pem)
      sshkey_bucket=''' + sshkey_bucket + '''
      gsutil cp ./lcm_pem.pub gs://$sshkey_bucket/
      popd

      # Set up cluster in OpsCenter the LCM way
      cd ~ubuntu/dse-gcp-install-$release

      # Generate cluster name
      cluster_name=''' + cluster_name + '''

      # Generate cluster size
      cluster_size=''' + str(cluster_size) + '''
    
      # DSE version
      dse_version=''' + dse_version + '''
 
      # Generate cassandra user's password
      db_pwd=''' + db_pwd + '''

      # Generate DataStax Academy credentials
      dsa_username=''' + dsa_username + '''
      dsa_password=''' + dsa_password + '''

      # Retrieve OpsCenter's public IP address
      private_ip=`echo $(hostname -I)`
      
      sleep 1m

      ./setupCluster.py --user ubuntu --pause 60 --opscpw $opsc_admin_pwd --trys 40 --opsc-ip $private_ip --clustername $cluster_name --privkey $privkey --datapath /mnt/data1 --repouser $dsa_username --repopw $dsa_password --dbpasswd $db_pwd --dsever $dse_version
      ./triggerInstall.py --opsc-ip $private_ip --opscpw $opsc_admin_pwd --clustername $cluster_name --clustersize $cluster_size 
      ./waitForJobs.py --num 1 --opsc-ip $private_ip --opscpw $opsc_admin_pwd

      # Alter required keyspaces for multi-DC
      ./alterKeyspaces.py --opscpw $opsc_admin_pwd --delay 60 >> ../../repair.log &

      # Remove public key from Google cloud storage bucket
      gsutil rm gs://$sshkey_bucket/lcm_pem.pub
  
      '''

    opscenter_node = {
        'name': opscenter_node_name,
        'type': 'compute.v1.instance',
        'properties': {
          'tags': {
                    'items': [
                       deployment, deployment + '-opscenter-vm'
                   ]
          },
          'zone': opscenter_zone,
          'machineType': opscenter_machine_type,
          'networkInterfaces': [{
                    'network': network,
                    'subnetwork': subnet,
                    'accessConfigs': [{
                        'name': 'External NAT',
                        'type': 'ONE_TO_ONE_NAT'
                    }]
          }],
          'disks': [{
                    'deviceName': 'boot-disk',
                    'type': 'PERSISTENT',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage':
                            URL_BASE + 'datastax-public/global/images/datastax-enterprise-ubuntu-1604-xenial-v20180824',
                        'diskType': opscenter_vm_disk_type
                    }
          }],
        'serviceAccounts': [{
                   'email': serviceAccountEmail,
                   'scopes': ['https://www.googleapis.com/auth/compute', 'https://www.googleapis.com/auth/cloudruntimeconfig', 'https://www.googleapis.com/auth/devstorage.full_control']
        }],
        'metadata': {
            'dependsOn': [
               sshkey_bucket,
            ],
            'items': [{
                'key': 'startup-script',
                'value': opscenter_script
            }]
          }
       }
    }

    config['resources'].append(opscenter_node)

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

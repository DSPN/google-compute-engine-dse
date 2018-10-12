import yaml
import random
import string


def GenerateConfig(context):
    config = {'resources': []}

    # Set zone property to match ops center zone. Needed for calls to common.MakeGlobalComputeLink.
    context.properties['zone'] = context.properties['opsCenterZone']
    cluster_name = context.properties['clusterName']

    # Generate a random bucket name
    bucket_suffix = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in xrange(10)])
    sshkey_bucket = context.env['deployment'] + '-ssh-pub-key-bucket-' + bucket_suffix

    # DSE version
    dse_version = context.properties['dseVersion']

    # Set cassandra's user password
    db_pwd = context.properties['cassandraPwd']

    # Set DataStax Academy credentials
    dsa_username = context.properties['dsa_username']
    dsa_password = context.properties['dsa_password']

    # Set default OpsCenter Admin password
    opsc_admin_pwd = context.properties['opsCenterAdminPwd']

    # Set cluster's size
    cluster_size = sum(context.properties['dcSize'])

    seed_nodes_dns_names = context.env['deployment'] + '-' + context.properties['zones'][0] + '-1-vm.c.' + context.env[
        'project'] + '.internal.'
    opscenter_node_name = context.env['deployment'] + '-opscenter-vm'
    opscenter_dns_name = opscenter_node_name + '.c.' + context.env['project'] + '.internal.'

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
        mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/google-${HOSTNAME}-data-disk
        mount -o discard,defaults /dev/disk/by-id/google-${HOSTNAME}-data-disk /mnt
        echo "/dev/disk/by-id/google-${HOSTNAME}-data-disk /mnt ext4 discard,defaults 0 2" | tee -a /etc/fstab
        mkdir -p /mnt/data1
        mkdir -p /mnt/data1/data
        mkdir -p /mnt/data1/saved_caches
        mkdir -p /mnt/data1/commitlog
        chmod -R 777 /mnt/data1

        ##### Install DSE the LCM way
        cd ~ubuntu
        release="7.0.3"
        wget https://github.com/DSPN/install-datastax-ubuntu/archive/$release.tar.gz
        tar -xvf $release.tar.gz
        # install extra OS packages
        pushd install-datastax-ubuntu-$release/bin
        ./os/extra_packages.sh
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

        cd ~ubuntu/install-datastax-ubuntu-$release/bin/lcm/

        ./addNode.py \
        --opsc-ip $opsc_ip \
        --clustername $cluster_name \
        --dcname $data_center_name \
        --rack $rack \
        --pubip $private_ip \
        --privip $private_ip \
        --nodeid $node_id \
        '''

    # Create DSE VM in each region
    count = 0
    for dc_size in context.properties['dcSize']:
      context.properties['current_zone'] = list()
      context.properties['current_zone'].append(context.properties['zones'][count])
      zonal_clusters = {
          'name': context.env['name'] + context.properties['current_zone'][0],
          'type': 'regional_multi_vm.py',
          'properties': {
              'sourceImage': 'https://www.googleapis.com/compute/v1/projects/datastax-public/global/images/datastax-enterprise-ubuntu-1604-xenial-v20180424',
              'zones': context.properties['current_zone'],
              'machineType': context.properties['machineType'],
              'network': context.properties['network'],
              'subnetwork': context.properties['subnetworks'][count],
              'numberOfVMReplicas': dc_size,
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
              'bootDiskSizeGb': 20,
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
      config['resources'].append(zonal_clusters)
      count += 1


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
      release="7.0.3" 
      wget https://github.com/DSPN/install-datastax-ubuntu/archive/$release.tar.gz
      tar -xvf $release.tar.gz
      # install extra OS packages
      pushd install-datastax-ubuntu-$release/bin
      ./os/extra_packages.sh
      ./os/install_java.sh
      cloud_type="gce"
      ./opscenter/install.sh $cloud_type
      ./opscenter/start.sh
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
      cd ~ubuntu/install-datastax-ubuntu-$release/bin/lcm/

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

      ./setupCluster.py --user ubuntu --pause 60 --trys 40 --opsc-ip $private_ip --clustername $cluster_name --privkey $privkey --datapath /mnt/data1 --repouser $dsa_username --repopw $dsa_password --dbpasswd $db_pwd --dsever $dse_version
      ./triggerInstall.py --opsc-ip $private_ip --clustername $cluster_name --clustersize $cluster_size 
      ./waitForJobs.py --num 1 --opsc-ip $private_ip 

      # Alter required keyspaces for multi-DC
      ./alterKeyspaces.py

      # Update password for default DSE OpsCenter administrator (admin)
      # opsCenterAdminPwd
      opsc_admin_pwd=''' + opsc_admin_pwd + '''
      cd ../opscenter
      ./set_opsc_pw_https.sh $opsc_admin_pwd

      # Remove public key from Google cloud storage bucket
      gsutil rm gs://$sshkey_bucket/lcm_pem.pub
  
      '''

    opscenter_node_name = context.env['deployment'] + '-opscenter-vm'
    opscenter_node = {
        'name': opscenter_node_name,
        'type': 'vm_instance.py',
        'properties': {
            'instanceName': opscenter_node_name,
            'sourceImage': 'https://www.googleapis.com/compute/v1/projects/datastax-public/global/images/datastax-enterprise-ubuntu-1604-xenial-v20180424',
            'zone': context.properties['opsCenterZone'],
            'machineType': context.properties['machineType'],
            'network': context.properties['network'],
            'subnetwork': context.properties['opsCenterSubnetwork'],
            'bootDiskType': 'pd-standard',
            'serviceAccounts': [{
                'email': 'default',
                'scopes': ['https://www.googleapis.com/auth/compute', 'https://www.googleapis.com/auth/devstorage.full_control']
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

    config['resources'].append(opscenter_node)

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

# Copyright 2019 DataStax, Inc. All rights reserved.

from __future__ import absolute_import
import common
import yaml
import random
import string
from six.moves import range

URL_BASE = 'https://www.googleapis.com/compute/v1/projects/'


def GenerateConfig(context):
    """Generates the configuration."""

    config = {'resources': []}

    zones = {
        "asia-east1": ["asia-east1-a", "asia-east1-b", "asia-east1-c"],
        "asia-east2": ["asia-east2-a", "asia-east2-b", "asia-east2-c"],
        "asia-northeast1": ["asia-northeast1-a", "asia-northeast1-b", "asia-northeast1-c"],
        "asia-northeast2": ["asia-northeast2-a", "asia-northeast2-b", "asia-northeast2-c"],
        "asia-northeast3": ["asia-northeast3-a", "asia-northeast3-b", "asia-northeast3-c"],
        "asia-south1": ["asia-south1-a", "asia-south1-b", "asia-south1-c"],
        "asia-southeast1": ["asia-southeast1-a", "asia-southeast1-b", "asia-southeast1-c"],
        "australia-southeast1": ["australia-southeast1-a", "australia-southeast1-b", "australia-southeast1-c"],
        "europe-north1": ["europe-north1-a", "europe-north1-b", "europe-north1-c"],
        "europe-west1": ["europe-west1-b", "europe-west1-c", "europe-west1-d"],
        "europe-west2": ["europe-west2-a", "europe-west2-b", "europe-west2-c"],
        "europe-west3": ["europe-west3-a", "europe-west3-b", "europe-west3-c"],
        "europe-west4": ["europe-west4-a", "europe-west4-b", "europe-west4-c"],
        "europe-west6": ["europe-west6-a", "europe-west6-b", "europe-west6-c"],
        "northamerica-northeast1": ["northamerica-northeast1-a", "northamerica-northeast1-b", "northamerica-northeast1-c"],
        "southamerica-east1": ["southamerica-east1-a", "southamerica-east1-b", "southamerica-east1-c"],
        "us-central1": ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"],
        "us-west1": ["us-west1-a", "us-west1-b", "us-west1-c"],
        "us-west2": ["us-west2-a", "us-west2-b", "us-west2-c"],
        "us-west3": ["us-west3-a", "us-west3-b", "us-west3-c"],
        "us-east1": ["us-east1-b", "us-east1-c", "us-east1-d"],
        "us-east4": ["us-east4-a", "us-east4-b", "us-east4-c"]
    }

    cassandraSkuImageMap = {
        "cassandra-68": "datastax-public/global/images/dse-ent-68-vm",
    }

    deployment = context.env['deployment']
    serviceAccountEmail = context.env['project_number'] + '-compute@developer.gserviceaccount.com'
    # TODO
    cassandraSku = "cassandra-68"
    gcp_region   = context.properties['region']
    cluster_size = str(context.properties['clusterSize'])
    dse_version  = str(context.properties['dseVersion'])
    disk_size    = str(context.properties['dataDiskSize'])

    # GCP Instance Templates
    cassandra_non_seed_it = deployment + '-cassandra-non-seed-it'

    # Cassandra seed_0 config
    cassandra_seed_0_vm_zone = zones[gcp_region][random.randint(0, len(zones[gcp_region])-1)]
    cassandra_seed_0_vm_name = deployment + '-cassandra-seed-0'
    cassandra_seed_0_vm_machine_type = ''.join([URL_BASE,
                                                context.env['project'], '/zones/',
                                                cassandra_seed_0_vm_zone, '/machineTypes/',
                                                context.properties['machineType']])
    cassandra_seed_0_vm_disk_type = ''.join([URL_BASE,
                                            context.env['project'], '/zones/',
                                            cassandra_seed_0_vm_zone, '/diskTypes/pd-ssd'])

    # Cassandra seed_1 config
    # seed_1 will deploy in a zone different than seed_0's zone
    temp_zones = zones[gcp_region][:]
    temp_zones.remove(cassandra_seed_0_vm_zone)
    cassandra_seed_1_vm_zone = temp_zones[random.randint(0, len(temp_zones)-1)]
    cassandra_seed_1_vm_name = deployment + '-cassandra-seed-1'
    cassandra_seed_1_vm_machine_type = ''.join([URL_BASE,
                                                context.env['project'], '/zones/',
                                                cassandra_seed_1_vm_zone, '/machineTypes/',
                                                context.properties['machineType']])
    cassandra_seed_1_vm_disk_type = ''.join([URL_BASE,
                                            context.env['project'], '/zones/',
                                            cassandra_seed_1_vm_zone, '/diskTypes/pd-ssd'])

    # GCP Instance Group Manager for Cassandra non-seed nodes
    cassandra_non_seed_igm = deployment + '-cassandra-non-seed-igm'

    # DevOps vm config
    dev_ops_vm_zone = zones[gcp_region][random.randint(0, len(zones[gcp_region])-1)]
    dev_ops_vm_name = deployment + '-cassandra-devops-vm'
    dev_ops_vm_machine_type = ''.join([URL_BASE,
                                        context.env['project'], '/zones/',
                                        dev_ops_vm_zone, '/machineTypes/',
                                        context.properties['devOpsMachineType']])
    dev_ops_vm_disk_type = ''.join([URL_BASE,
                                    context.env['project'], '/zones/',
                                    dev_ops_vm_zone, '/diskTypes/pd-ssd'])

    # GCP subnet
    # Set Cassandra subnet's CIDR to 10.8.0.0/16
    cidr                          = '10.8.0.0/16'
    cassandra_subnet              = deployment + '-cassandra-subnet-' + gcp_region
    cassandra_network_name_suffix = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(6)])
    cassandra_network_name        = deployment + '-' + cassandra_network_name_suffix
    cassandra_network             = URL_BASE + context.env['project'] + '/global/networks/' + cassandra_network_name

    # Cassandra firewall
    cassandra_fw_allow_all_int_10_network = deployment + '-cassandra-fw-allow-10-network'
    cassandra_fw_allow_ssh                = deployment + '-cassandra-fw-allow-ssh'
    cassandra_fw_allow_devops_vm_8080     = deployment + '-cassandra-fw-allow-8080'
    cassandra_fw_allow_9042               = deployment + '-cassandra-fw-allow-9042'

    # Cassandra Cloud NAT
    router_name     = context.env['deployment'] + '-router'
    cassandra_route = context.env['deployment'] + '-cassandra-route'

    # Cassandra accessConfig
    cassandra_access_configs = []
    allow_9042_fw = {}
    if context.properties['extIP']:
        cassandra_access_configs = [{
            'name': 'External NAT',
            'type': 'ONE_TO_ONE_NAT'
        }]
        allow_9042_fw = {
            'name': cassandra_fw_allow_9042,
            'type': 'compute.v1.firewalls',
            'properties': {
                'name': cassandra_fw_allow_9042,
                'description': 'firewall rule to access C* node on port 9042',
                'network': cassandra_network,
                'targetTags': [
                    deployment + '-cassandra-node'
                ],
                'sourceRanges': [
                    "0.0.0.0/0"
                ],
                'allowed': [{
                    'IPProtocol': 'TCP',
                    'ports': ["9042"]
                }]
            },
            'metadata': {
                'dependsOn': [
                    cassandra_network_name,
                ]
            }
        }

    # Cassandra seed 0 and seed 1 IP addresses on .3 and .4
    int_ip_octet             = cidr.split(".")
    int_ip_prefix            = int_ip_octet[0] + "." + int_ip_octet[1] + "." + int_ip_octet[2]
    cassandra_seed_0_ip_addr = int_ip_prefix + ".3"
    cassandra_seed_1_ip_addr = int_ip_prefix + ".4"
    opscip                   = int_ip_prefix + ".2"
    seeds                    = cassandra_seed_0_ip_addr + ',' + cassandra_seed_1_ip_addr

    # Cassandra cluster info
    cluster_name = context.properties['clusterName']
    cluster_size = str(context.properties['clusterSize'])
    dc_name      = context.properties['dcName']
    dse_version  = context.properties['dseVersion']
    public_ips   = str(context.properties['extIP'])

    # 1800 seconds for solution deployment timeout
    cassandra_timeout = 1800

    # Generate a random bucket name for each deployment
    bucket_suffix = ''.join(
        [random.choice(string.ascii_lowercase + string.digits) for n in range(10)])
    deployment_bucket = context.env['deployment'] + '-' + bucket_suffix

    # Check Cassandra cluster ready script
    check_cassandra_cluster_ready_script = '''
    #!/usr/bin/env bash
    sudo echo "********** check_cassandra_cluster_ready_script **********" >> /var/log/syslog
    SUB="cassandra_metrics"
    sudo echo "$cluster_name" >> /var/log/syslog
    output=$(curl "http://10.8.0.2:8888/cluster-configs")
    if [[ "$output" == *"$SUB"* ]]; then
        exit 0
    fi
    exit 1
    '''

    # Check OPSC ready script
    check_opsc_ready_script = '''
    #!/usr/bin/env bash
    sudo echo "********** check_opsc_ready_script **********" >> /var/log/syslog
    nc -z -v -w5 10.8.0.2 8888
    if [ $? -ne 0 ]; then
        exit 1
    fi
    exit 0
    '''

    # Cassandra seed node 0 startup script
    cassandra_seed_0_script = '''
    #!/usr/bin/env bash

    sudo chmod -R ug+w /home/dse

    sudo echo "********** cassandra_seed_0_script **********" >> /var/log/syslog

    # If Cassandra is already installed, do nothing
    systemctl is-enabled cassandra
    retVal=$?
    if [ $retVal -eq 0 ]; then
        exit 0
    fi


    dse_version=''' + dse_version + '''
    sudo echo "********** dse_version ********** "+$dse_version >> /var/log/syslog

    ## Download binaries
    pushd /home/dse
    if [ "$dse_version" = "6.8.1" ]; then
        gsutil cp gs://dse-opsc-vm-components/dse-6.8.1-bin.tar.gz /home/dse
    else
        gsutil cp gs://dse-opsc-vm-components/dse-5.1.18-bin.tar.gz /home/dse
    fi

    while [ $? -ne 0 ]
    do
        sleep 10s
        if [ "$dse_version" = "6.8.1" ]; then
            gsutil cp gs://dse-opsc-vm-components/dse-6.8.1-bin.tar.gz /home/dse
        else
            gsutil cp gs://dse-opsc-vm-components/dse-5.1.18-bin.tar.gz /home/dse
        fi

    done

    gsutil cp gs://dse-opsc-vm-components/datastax-agent-6.8.0.tar.gz /home/dse

    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://dse-opsc-vm-components/datastax-agent-6.8.0.tar.gz /home/dse

    done

    gsutil cp gs://dse-opsc-vm-components/cassandra.service /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/cassandra.service /home/dse
    done

    gsutil cp gs://dse-opsc-vm-components/cassconf /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/cassconf /home/dse
    done
    gsutil cp gs://dse-opsc-vm-components/start-cassandra /home/dse

    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/start-cassandra /home/dse
    done

    gsutil cp gs://dse-opsc-vm-components/stop-cassandra /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/stop-cassandra /home/dse
    done

    cd /usr/share
    mkdir dse


    popd


    # Ansible-way
    deployment_bucket=''' + deployment_bucket + '''
    gsutil cp gs://$deployment_bucket/id_rsa.pub /home/ubuntu/.ssh/
    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://$deployment_bucket/id_rsa.pub /home/ubuntu/.ssh/
    done
    mv /home/ubuntu/.ssh/authorized_keys /home/ubuntu/.ssh/authorized_keys.bak
    cat /home/ubuntu/.ssh/id_rsa.pub >> /home/ubuntu/.ssh/authorized_keys
    chown -R ubuntu:ubuntu /home/ubuntu/.ssh
    chown ubuntu:ubuntu /home/ubuntu/.ssh/*

    '''

    # Cassandra seed node 1 startup script
    cassandra_seed_1_script = '''
    #!/usr/bin/env bash

    sudo chmod -R ug+w /home/dse

    # If Cassandra is already installed, do nothing
    systemctl is-enabled cassandra
    retVal=$?
    if [ $retVal -eq 0 ]; then
    exit 0
    fi

    dse_version=''' + dse_version + '''

    ## Install binary
    pushd /home/dse
    if [ "$dse_version" = "6.8.1" ]; then
        gsutil cp gs://dse-opsc-vm-components/dse-6.8.1-bin.tar.gz /home/dse
    else
        gsutil cp gs://dse-opsc-vm-components/dse-5.1.18-bin.tar.gz /home/dse
    fi

    while [ $? -ne 0 ]
    do
        sleep 10s
        if [ "$dse_version" = "6.8.1" ]; then
            gsutil cp gs://dse-opsc-vm-components/dse-6.8.1-bin.tar.gz /home/dse
        else
            gsutil cp gs://dse-opsc-vm-components/dse-5.1.18-bin.tar.gz /home/dse
        fi

    done

    gsutil cp gs://dse-opsc-vm-components/datastax-agent-6.8.0.tar.gz /home/dse

    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://dse-opsc-vm-components/datastax-agent-6.8.0.tar.gz /home/dse

    done

    gsutil cp gs://dse-opsc-vm-components/cassandra.service /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/cassandra.service /home/dse
    done

    gsutil cp gs://dse-opsc-vm-components/cassconf /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/cassconf /home/dse
    done
    gsutil cp gs://dse-opsc-vm-components/start-cassandra /home/dse

    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/start-cassandra /home/dse
    done

    gsutil cp gs://dse-opsc-vm-components/stop-cassandra /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/stop-cassandra /home/dse
    done


    cd /usr/share
    mkdir dse

    popd

    # If Cassandra is already installed, do nothing
    systemctl is-enabled cassandra
    retVal=$?
    if [ $retVal -eq 0 ]; then
    exit 0
    fi

    # Ansible-way
    deployment_bucket=''' + deployment_bucket + '''
    gsutil cp gs://$deployment_bucket/id_rsa.pub /home/ubuntu/.ssh/
    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://$deployment_bucket/id_rsa.pub /home/ubuntu/.ssh/
    done
    mv /home/ubuntu/.ssh/authorized_keys /home/ubuntu/.ssh/authorized_keys.bak
    cat /home/ubuntu/.ssh/id_rsa.pub >> /home/ubuntu/.ssh/authorized_keys
    chown -R ubuntu:ubuntu /home/ubuntu/.ssh
    chown ubuntu:ubuntu /home/ubuntu/.ssh/*


    # Cleanup

    '''

    # Cassandra non-seed nodes startup script
    cassandra_non_seed_script = '''
    #!/usr/bin/env bash

    # If Cassandra is already installed, do nothing
    systemctl is-enabled cassandra
    retVal=$?
    if [ $retVal -eq 0 ]; then
        exit 0
    fi

    sudo echo "********** cassandra_non_seed_script **********" >> /var/log/syslog

    sudo chmod -R ug+w /home/dse
    chown -R ubuntu:ubuntu /home/ubuntu/.ssh

    dse_version=''' + dse_version + '''
    ## Install binary
    pushd /home/dse
    if [ "$dse_version" = "6.8.1" ]; then
        gsutil cp gs://dse-opsc-vm-components/dse-6.8.1-bin.tar.gz /home/dse
    else
        gsutil cp gs://dse-opsc-vm-components/dse-5.1.18-bin.tar.gz /home/dse
    fi

    while [ $? -ne 0 ]
    do
        sleep 10s
        if [ "$dse_version" = "6.8.1" ]; then
            gsutil cp gs://dse-opsc-vm-components/dse-6.8.1-bin.tar.gz /home/dse
        else
            gsutil cp gs://dse-opsc-vm-components/dse-5.1.18-bin.tar.gz /home/dse
        fi

    done

    sudo echo "********** dse tarball downloaded **********" >> /var/log/syslog

    gsutil cp gs://dse-opsc-vm-components/datastax-agent-6.8.0.tar.gz /home/dse

    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://dse-opsc-vm-components/datastax-agent-6.8.0.tar.gz /home/dse

    done

    gsutil cp gs://dse-opsc-vm-components/cassandra.service /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/cassandra.service /home/dse
    done

    gsutil cp gs://dse-opsc-vm-components/cassconf /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/cassconf /home/dse
    done
    gsutil cp gs://dse-opsc-vm-components/start-cassandra /home/dse

    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/start-cassandra /home/dse
    done

    gsutil cp gs://dse-opsc-vm-components/stop-cassandra /home/dse
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp gs://dse-opsc-vm-components/stop-cassandra /home/dse
    done

    sudo echo "********** dse agent downloaded **********" >> /var/log/syslog

    cd /usr/share
    mkdir dse

    popd

    # Ansible-way
    deployment_bucket=''' + deployment_bucket + '''
    gsutil cp gs://$deployment_bucket/id_rsa.pub /home/ubuntu/.ssh/
    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://$deployment_bucket/id_rsa.pub /home/ubuntu/.ssh/
    done
    mv /home/ubuntu/.ssh/authorized_keys /home/ubuntu/.ssh/authorized_keys.bak
    cat /home/ubuntu/.ssh/id_rsa.pub >> /home/ubuntu/.ssh/authorized_keys
    chown -R ubuntu:ubuntu /home/ubuntu/.ssh
    chown ubuntu:ubuntu /home/ubuntu/.ssh/*

    sudo echo "********** ssh keys added  **********" >> /var/log/syslog

    # Cleanup

    '''

    devops_vm_script = '''
    #!/usr/bin/env bash

    sudo echo "********** devops_vm_script **********" >> /var/log/syslog

    sudo mkdir /home/dse
    sudo mkdir /home/dse
    sudo chmod -R ug+w /home/dse

    # Ansible way
    deployment_bucket=''' + deployment_bucket + '''
    ssh-keygen -t rsa -N "" -f /home/ubuntu/.ssh/id_rsa
    gsutil cp /home/ubuntu/.ssh/id_rsa.pub gs://$deployment_bucket/
    while [ $? -ne 0 ]
    do
        sleep 5s
        gsutil cp /home/ubuntu/.ssh/id_rsa.pub gs://$deployment_bucket/
    done

    mv /home/ubuntu/.ssh/authorized_keys /home/ubuntu/.ssh/authorized_keys.bak
    cat /home/ubuntu/.ssh/id_rsa.pub >> /home/ubuntu/.ssh/authorized_keys
    chmod 0600 /home/ubuntu/.ssh/authorized_keys
    chown -R ubuntu:ubuntu /home/ubuntu/.ssh
    chown ubuntu:ubuntu /home/ubuntu/.ssh/*

    # TODO

    ## Install binary
    pushd /home/dse
    gsutil cp gs://dse-opsc-vm-components/opscenter-6.8.0.tar.gz /home/dse
    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://dse-opsc-vm-components/opscenter-6.8.0.tar.gz /home/dse

    done

    gsutil cp gs://dse-opsc-vm-components/*.yml /home/dse
    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://dse-opsc-vm-components/*.yml /home/dse

    done

    gsutil cp gs://dse-opsc-vm-components/ansible-hosts.cfg /home/dse
    while [ $? -ne 0 ]
    do
        sleep 10s
        gsutil cp gs://dse-opsc-vm-components/ansible-hosts.cfg /home/dse
        gsutil cp gs://dse-opsc-vm-components/ansible.cfg /home/dse
    done

    cd /home/dse
    popd

    cluster_name=''' + cluster_name + '''
    dc_name=''' + dc_name + '''
    seed0_seeds=''' + cassandra_seed_0_ip_addr + '''
    seeds=''' + seeds + '''
    disksize=''' + disk_size + '''
    cluster_size=''' + cluster_size + '''
    public_ips=''' + public_ips + '''
    opscip=''' + opscip + '''
    dse_version=''' + dse_version + '''

    # TODO
    #

    index=5
    until [ $cluster_size -lt 3 ]; do
        let cluster_size-=1
        echo 10.8.0.$(( index++ )) >> /home/dse/ansible-hosts.cfg
    done

    export ANSIBLE_HOST_KEY_CHECKING=False
    pushd /home/dse

    chown -R ubuntu:ubuntu /home/ubuntu/.ssh
    cp /home/dse/ansible.cfg /etc/ansible/ansible.cfg

    # check if seed node is up
    nc -z -v -w5 10.8.0.3 22
    while [ $? -ne 0 ]
    do
        sleep 5s
        nc -z -v -w5 10.8.0.3 22
    done

    # Seed 0

    su - ubuntu
    #
    sleep 60s
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/os-config.yml --extra-vars "host=CASSANDRA_SEED_0"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/ebs-init.yml --extra-vars "host=CASSANDRA_SEED_0"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/cassandra-directories.yml --extra-vars "host=CASSANDRA_SEED_0"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/cassandra-install.yml --extra-vars "host=CASSANDRA_SEED_0 disksize=$disksize cluster_name=$cluster_name dc=$dc_name seeds=$seed0_seeds public_ips=$public_ips opscip=$opscip dse_version=$dse_version"

        # Seed 1
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/os-config.yml --extra-vars "host=CASSANDRA_SEED_1"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/ebs-init.yml --extra-vars "host=CASSANDRA_SEED_1"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/cassandra-directories.yml --extra-vars "host=CASSANDRA_SEED_1"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/cassandra-install.yml --extra-vars "host=CASSANDRA_SEED_1 disksize=$disksize cluster_name=$cluster_name dc=$dc_name seeds=$seeds public_ips=$public_ips opscip=$opscip dse_version=$dse_version"

        # Non Seed Nodes
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/os-config.yml -f 30 --extra-vars "host=CASSANDRA_NON_SEED_NODES"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/ebs-init.yml -f 30 --extra-vars  "host=CASSANDRA_NON_SEED_NODES"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/cassandra-directories.yml -f 30 --extra-vars "host=CASSANDRA_NON_SEED_NODES"
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/cassandra-install.yml -f 30 --extra-vars "host=CASSANDRA_NON_SEED_NODES disksize=$disksize cluster_name=$cluster_name dc=$dc_name seeds=$seeds public_ips=$public_ips opscip=$opscip dse_version=$dse_version"

    # OpsCenter
    ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/opscenter-install.yml --extra-vars "seeds=$seeds cluster_name=$cluster_name"

    # Remove keys
    #ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/os-removekeys.yml --extra-vars "host=CASSANDRA_SEED_0"
    #ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/os-removekeys.yml --extra-vars "host=CASSANDRA_SEED_1"
    #ansible-playbook -v -u ubuntu -i /home/dse/ansible-hosts.cfg --private-key /home/ubuntu/.ssh/id_rsa /home/dse/os-removekeys.yml --extra-vars "host=CASSANDRA_NON_SEED_NODES"

    # check if nodes are  up
    #echo "********** devops_vm_script  check nodes **********" >> /var/log/syslog

    #nc -z -v -w5 10.8.0.5 9042
    #while [ $? -ne 0 ]
    #do
    #  echo "********** devops_vm_script  check nodes port not open **********" >> /var/log/syslog
    #  sleep 5s
    #  nc -z -v -w5 10.8.0.5 9042
    #done

    #echo "********** devops_vm_script  check nodes done **********" >> /var/log/syslog

    # Cleanup

    #mv /home/ubuntu/.ssh/authorized_keys.bak /home/ubuntu/.ssh/authorized_keys
    #rm /home/dse/*.yml
    #rm /home/dse/*.cfg
    rm /home/dse/*.gz
    gsutil rm gs://$deployment_bucket/*

    '''

    # Create a dictionary which represents the resources
    resources = [
        {
            'name': deployment_bucket,
            'type': 'storage.v1.bucket',
            'properties': {
                'name': deployment_bucket,
                'lifecycle': {
                    "rule": [{
                        "action": {"type": "Delete"},
                        "condition": {"age": 1}
                    }]
                }
            }
        },
        {
            'name': cassandra_network_name,
            'type': 'compute.v1.network',
            'properties': {
                'name': cassandra_network_name,
                'description': 'VPC network for Cassandra cluster deployment',
                'autoCreateSubnetworks': False,
            }
        },
        {
            'name': cassandra_subnet,
            'type': 'compute.v1.subnetwork',
            'properties': {
                'name': cassandra_subnet,
                'description': 'Subnetwork of %s in %s' % (cassandra_network_name, cassandra_subnet),
                'ipCidrRange': cidr,
                'region': gcp_region,
                'network': cassandra_network,
            },
            'metadata': {
                'dependsOn': [
                    cassandra_network_name,
                ]
            }
        },
        {
            'name': cassandra_fw_allow_all_int_10_network,
            'type': 'compute.v1.firewalls',
            'properties': {
                'name': cassandra_fw_allow_all_int_10_network,
                'description': 'firewall rule to allow all access inside 10.x.x.x network',
                'network': cassandra_network,
                'sourceRanges': [
                    "10.0.0.0/8"
                ],
                'allowed': [{
                    'IPProtocol': 'TCP',
                    'ports': ["0-65535"]
                },
                    {
                    'IPProtocol': 'UDP',
                    'ports': ["0-65535"]
                },
                    {
                    'IPProtocol': 'ICMP'
                }]
            },
            'metadata': {
                'dependsOn': [
                    cassandra_network_name,
                ]
            }
        },
        {
            'name': cassandra_fw_allow_ssh,
            'type': 'compute.v1.firewalls',
            'properties': {
                'name': cassandra_fw_allow_ssh,
                'description': 'firewall rule to enable ssh',
                'network': cassandra_network,
                'sourceRanges': [
                    "0.0.0.0/0"
                ],
                'allowed': [{
                    'IPProtocol': 'TCP',
                    'ports': ["22"]
                }]
            },
            'metadata': {
                'dependsOn': [
                    cassandra_network_name,
                ]
            }
        },
        {
            'name': cassandra_fw_allow_devops_vm_8080,
            'type': 'compute.v1.firewalls',
            'properties': {
                'name': cassandra_fw_allow_devops_vm_8080,
                'description': 'firewall rule to enable 8080 on devOps VM',
                'network': cassandra_network,
                'targetTags': [
                    deployment + '-devops-vm'
                ],
                'sourceRanges': [
                    "0.0.0.0/0"
                ],
                'allowed': [{
                    'IPProtocol': 'TCP',
                    'ports': ["8888"]
                }]
            },
            'metadata': {
                'dependsOn': [
                    cassandra_network_name,
                ]
            }
        },
        {
            'name': router_name,
            'type': 'compute.v1.router',
            'properties': {
                'description': 'Cloud Route for Cassandra',
                'network': cassandra_network,
                'region': gcp_region,
                'nats': [
                    {
                        'logConfig': {
                            'enable': False,
                            'filter': 'ALL'
                        },
                        'name': cassandra_route,
                        'natIpAllocateOption': 'AUTO_ONLY',
                        'sourceSubnetworkIpRangesToNat': 'ALL_SUBNETWORKS_ALL_PRIMARY_IP_RANGES'
                    }
                ],
            },
            'metadata': {
                'dependsOn': [
                    cassandra_network_name,
                ]
            }
        },
        {
            'name': 'software-status',
            'type': 'software_status.py',
            'properties': {
                'timeout': cassandra_timeout,
                'waiterDependsOn': [
                    cassandra_seed_0_vm_name
                ]
            }
        },
        {
            'name': 'cassandra-software-status-script',
            'type': 'software_status_script.py',
            'properties': {
                'initScript': cassandra_seed_0_script,
                'checkScript': check_cassandra_cluster_ready_script
            }
        },
        {
            'name': cassandra_seed_0_vm_name,
            'type': 'compute.v1.instance',
            'properties': {
                'tags': {
                    'items': [
                        deployment, deployment + '-cassandra-node'
                    ]
                },
                'zone': cassandra_seed_0_vm_zone,
                'machineType': cassandra_seed_0_vm_machine_type,
                'networkInterfaces': [{
                    'network': cassandra_network,
                    'subnetwork': '$(ref.%s.selfLink)' % cassandra_subnet,
                    'networkIP': '10.8.0.3',
                    'accessConfigs': cassandra_access_configs
                }],
                'disks': [{
                    'deviceName': 'boot-disk',
                    'type': 'PERSISTENT',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': URL_BASE + cassandraSkuImageMap[cassandraSku],
                        'diskType': cassandra_seed_0_vm_disk_type
                    }
                },
                    {
                    'deviceName': 'vm-data-disk',
                    'type': 'PERSISTENT',
                    'boot': False,
                    'autoDelete': True,
                    'initializeParams': {
                        'diskType': cassandra_seed_0_vm_disk_type,
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
                        cassandra_subnet,
                    ],
                    'items': [{
                        'key': 'startup-script',
                        'value': '$(ref.cassandra-software-status-script.startup-script)'
                    },
                        {
                        'key': 'status-config-url',
                        'value': '$(ref.software-status.config-url)'
                    },
                        {
                        'key': 'status-variable-path',
                        'value': '$(ref.software-status.variable-path)'
                    },
                        {
                        'key': 'status-uptime-deadline',
                        'value': cassandra_timeout
                    }]
                }
            }
        },
        {
            'name': cassandra_seed_1_vm_name,
            'type': 'compute.v1.instance',
            'properties': {
                'tags': {
                    'items': [
                        deployment, deployment + '-cassandra-node'
                    ]
                },
                'zone': cassandra_seed_1_vm_zone,
                'machineType': cassandra_seed_1_vm_machine_type,
                'networkInterfaces': [{
                    'network': cassandra_network,
                    'subnetwork': '$(ref.%s.selfLink)' % cassandra_subnet,
                    'networkIP': '10.8.0.4',
                    'accessConfigs': cassandra_access_configs
                }],
                'disks': [{
                    'deviceName': 'boot-disk',
                    'type': 'PERSISTENT',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': URL_BASE + cassandraSkuImageMap[cassandraSku],
                        'diskType': cassandra_seed_1_vm_disk_type
                    }
                },
                    {
                    'deviceName': 'vm-data-disk',
                    'type': 'PERSISTENT',
                    'boot': False,
                    'autoDelete': True,
                    'initializeParams': {
                        'diskType': cassandra_seed_1_vm_disk_type,
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
                        cassandra_subnet,
                    ],
                    'items': [{
                        'key': 'startup-script',
                        'value': cassandra_seed_1_script
                    }]
                }
            }
        },
        {
            # Create the Instance Template
            'name': cassandra_non_seed_it,
            'type': 'compute.v1.instanceTemplate',
            'properties': {
                'properties': {
                    'tags': {
                        'items': [
                            deployment, deployment + '-cassandra-node'
                        ]
                    },
                    'machineType':
                        context.properties['machineType'],
                    'networkInterfaces': [{
                        'network': cassandra_network,
                        'subnetwork': '$(ref.%s.selfLink)' % cassandra_subnet,
                        'accessConfigs': cassandra_access_configs
                    }],
                    'disks': [{
                        'deviceName': 'boot-disk',
                        'type': 'PERSISTENT',
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': URL_BASE + cassandraSkuImageMap[cassandraSku]
                        }
                    },
                        {
                        'deviceName': 'vm-data-disk',
                        'type': 'PERSISTENT',
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskType': 'pd-ssd',
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
                            cassandra_subnet,
                        ],
                        'items': [{
                            'key': 'startup-script',
                            'value': cassandra_non_seed_script
                        }]
                    }
                }
            }
        },
        {
            'name': dev_ops_vm_name,
            'type': 'compute.v1.instance',
            'properties': {
                'tags': {
                    'items': [
                        deployment, deployment + '-devops-vm'
                    ]
                },
                'zone': dev_ops_vm_zone,
                'machineType': dev_ops_vm_machine_type,
                'networkInterfaces': [{
                    'network': cassandra_network,
                    'subnetwork': '$(ref.%s.selfLink)' % cassandra_subnet,
                    'networkIP': '10.8.0.2',
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
                                URL_BASE + 'datastax-public/global/images/dse-ent-68-vm',
                            'diskType': dev_ops_vm_disk_type
                    }
                }],
                'serviceAccounts': [{
                    'email': serviceAccountEmail,
                    'scopes': ['https://www.googleapis.com/auth/compute', 'https://www.googleapis.com/auth/cloudruntimeconfig', 'https://www.googleapis.com/auth/devstorage.full_control']
                }],
                'metadata': {
                    'dependsOn': [
                        cassandra_non_seed_igm,
                    ],
                    'items': [{
                        'key': 'startup-script',
                        'value': devops_vm_script
                    }]
                }
            }
        },
        {
            # Instance Group Manager
            'name': cassandra_non_seed_igm,
            'type': 'compute.v1.regionInstanceGroupManager',
            'properties': {
                'region': gcp_region,
                'baseInstanceName': deployment + '-cassandra-non-seed-node',
                'instanceTemplate': '$(ref.%s.selfLink)' % cassandra_non_seed_it,
                'targetSize': context.properties['clusterSize'] - 2
            },
            'metadata': {
                'dependsOn': [
                    cassandra_non_seed_it,
                ]
            }
        }
    ]

    config['resources'] = resources
    if context.properties['extIP']:
        config['resources'].append(allow_9042_fw)

    outputs = [
        {
            'name': 'project',
            'value': context.env['project']
        },
        {
            'name': 'cassandraSku',
            'value': cassandraSku
        },
        {
            'name': 'gcp_region',
            'value': gcp_region
        },
        {
            'name': 'networkName',
            'value': cassandra_network_name
        },
        {
            'name': 'clusterName',
            'value': cluster_name
        },
        {
            'name': 'clusterSize',
            'value': cluster_size
        },
        {
            'name': 'dseVersion',
            'value': dse_version
        },
        {
            'name': 'dcName',
            'value': dc_name
        },
        {
            'name': 'devOpsName',
            'value': dev_ops_vm_name
        },
        {
            'name': 'devOpsSelfLink',
            'value': '$(ref.' + dev_ops_vm_name + '.selfLink)'
        },
        {
            'name': 'seed0Name',
            'value': cassandra_seed_0_vm_name
        },
        {
            'name': 'seed0SelfLink',
            'value': '$(ref.' + cassandra_seed_0_vm_name + '.selfLink)'
        },
        {
            'name': 'devOpsExtIP',
            'value':  '$(ref.' + dev_ops_vm_name + '.networkInterfaces[0].accessConfigs[0].natIP)'
        }
    ]
    config['outputs'] = outputs

    return yaml.dump(config)

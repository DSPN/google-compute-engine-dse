#!/usr/bin/env bash

INSTANCE=instance-1

# Create a raw image (tar file) on the newly attach disk and export the image file to Cloud Storage bucket.

# SSH into the instance:
gcloud compute ssh ${INSTANCE}

# Format and mount your new disk as /mnt/tmp
sudo mkdir /mnt/tmp
sudo /usr/share/google/safe_format_and_mount -m "mkfs.ext4 -F" /dev/sdb /mnt/tmp

# By default /dev/sdb is the default for mounted disk. You can check this via:
ls -l /dev/disk/by-id/google-*

# Create a Google Cloud Storage bucket if you do not already have one available
# Go to Google cloud developer console
# In the left nav, click on Storage -> Cloud Storage -> Browser
# In the right pane, click on ‘Create Bucket’, and create a bucket using ‘defaults’
##### This already exists and is called marketplaceimage

# From the VM instance, run gcloud command to package, creating a tar ball

# Name of the output filename for your disk image. By default it's an image size hex
INSTANCE=$(hostname)

# Creates a list of home dir to exclude
EXCLUDES=`python -c  "import os; print ','.join([os.path.join('/home', d) for d in os.listdir('/home')])"`

sudo su
apt-get update

# Install Java
echo "Installing the Oracle JDK"

# Install add-apt-repository
apt-get -y install software-properties-common

add-apt-repository -y ppa:webupd8team/java
apt-get -y update
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
apt-get -y install oracle-java8-installer

# Download, but do not install DataStax Enterprise
echo "deb http://datastax%40google.com:8GdeeVT2s7zi@debian.datastax.com/enterprise stable main" | sudo tee -a /etc/apt/sources.list.d/datastax.sources.list
curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -
apt-get -y update
dse_version=5.0.1-1
apt-get -y -d install dse-full=$dse_version dse=$dse_version dse-hive=$dse_version dse-pig=$dse_version dse-demos=$dse_version dse-libsolr=$dse_version dse-libtomcat=$dse_version dse-libsqoop=$dse_version dse-liblog4j=$dse_version dse-libmahout=$dse_version dse-libhadoop-native=$dse_version dse-libcassandra=$dse_version dse-libhive=$dse_version dse-libpig=$dse_version dse-libhadoop=$dse_version dse-libspark=$dse_version
opscenter_version=6.0.1
apt-get -y -d install datastax-agent=$opscenter_version opscenter=$opscenter_version

# To copy the image directly to a storage bucket use --bucket=BUCKET_NAME with the above command
# The image is stored as a raw block file, packaged and compressed using gzip and tar. The raw block file contains the OS and all installed packages, plus all files in the root persistent disk. It does not include files or packages in a non-root persistent disk.
# The image is stored at: /mnt/tmp/${INSTANCE}-image.tar.gz
sudo gcimagebundle -d /dev/sda -o /mnt/tmp --log_file=/tmp/export.log --output_file_name=datastax-image.tar.gz --excludes=$EXCLUDES

# Attach a Google License ID to the VM Image

# Untar the ${INSTANCE}-image.tar.gz to obtain disk.raw file
cd /mnt/tmp
tar -xvf datastax-image.tar.gz

## set the GCP project ID  and zone to gcloud
gcloud config set project datastax-dev
gcloud config set compute/zone us-central1-f

## In case the solution requires multiple license ids
wget https://raw.githubusercontent.com/DSPN/google-deployment-manager-create-base-vm/master/license_image.py

# Looks like the file this writes out to is always licensed-base-os-raw.tar.gz in the bucket
python license_image.py --disk disk.raw --bucket gs://marketplaceimage --licenses 1001300 1000010

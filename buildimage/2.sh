#!/usr/bin/env bash

# SSH into the instance
INSTANCE=instance-3
gcloud compute ssh ${INSTANCE}

sudo su

### Install Java
apt-get update
apt-get -y install software-properties-common
add-apt-repository -y ppa:webupd8team/java
apt-get update

echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections

# If you're going through all this trouble, you probably want to check you're using the latest packages
apt-cache policy oracle-java8-installer
java_version=123

# I should really try specifying version here...
apt-get -y install oracle-java8-installer=$java_version

### Download, but do not install DataStax Enterprise
echo "deb http://datastax%40google.com:8GdeeVT2s7zi@debian.datastax.com/enterprise stable main" | sudo tee -a /etc/apt/sources.list.d/datastax.sources.list
curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -
apt-get -y update

# If you're going through all this trouble, you probably want to check you're using the latest packages
apt-cache policy dse-full
dse_version=5.0.1-1

apt-cache policy opscenter
opscenter_version=6.0.2

# Download (but do not install) the DataStax packages
apt-get -y -d install dse-full=$dse_version dse=$dse_version dse-hive=$dse_version dse-pig=$dse_version dse-demos=$dse_version dse-libsolr=$dse_version dse-libtomcat=$dse_version dse-libsqoop=$dse_version dse-liblog4j=$dse_version dse-libmahout=$dse_version dse-libhadoop-native=$dse_version dse-libcassandra=$dse_version dse-libhive=$dse_version dse-libpig=$dse_version dse-libhadoop=$dse_version dse-libspark=$dse_version
apt-get -y -d install datastax-agent=$opscenter_version opscenter=$opscenter_version

# Halt the machine so the Google people can take the image
shutdown -h now

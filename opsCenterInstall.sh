#!/bin/bash
# This script installs Java and DataStax OpsCenter.  It then deploys a DataStax Enterprise cluster using OpsCenter.

echo "Installing Java"
apt-get update
apt-get -y install default-jre

echo "Installing OpsCenter"
echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/datastax.community.list
curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -
apt-get update
apt-get -y install opscenter

echo "Starting OpsCenter"
sudo service opscenterd start


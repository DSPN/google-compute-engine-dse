#!/usr/bin/env bash

# Run this from the local box ---- need to be logged into gcloud

#Create a VM image from the licensed tar file.
# Note: ${IMAGE_DESCRIPTION}  shouldn't be more than 40 chars.
IMAGE_DESCRIPTION="DataStax"
PROJECT_ID=datastax-public
INSTANCE=datastax
BUCKET_NAME=marketplaceimage
gcloud config set project datastax-dev
gcloud compute --project ${PROJECT_ID} images create ${INSTANCE} --description ${IMAGE_DESCRIPTION} --source-uri https://storage.googleapis.com/${BUCKET_NAME}/licensed-base-os-raw.tar.gz

#### this doesn't work right now because the image is in a different project

# Create a VM instance from the image to test
VM_instance_name=datastaxtestinstance
gcloud compute instances create ${VM_instance_name} --image ${INSTANCE}

# Verify license ID. SSH into the VM and run one of the following to see the attached license ID.
gcloud compute ssh ${VM_instance_name}
curl http://metadata/computeMetadata/v1beta1/instance/licenses/0/id
curl -s -H "Metadata-Flavor: Google" http://metadata/computeMetadata/v1beta1/instance/licenses/?recursive=true

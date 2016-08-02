#!/usr/bin/env bash

INSTANCE=instance-1

# Create a VM using one of the supported operating systems.
# Create a new instance with --scopes "storage-rw"
gcloud compute --project "datastax-dev" instances create ${INSTANCE} --zone "us-central1-f" --machine-type "n1-standard-8" --network "default" --maintenance-policy "MIGRATE" --scopes default="https://www.googleapis.com/auth/cloud-platform" --image "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1404-trusty-v20160314" --boot-disk-size "200" --boot-disk-type "pd-standard" --boot-disk-device-name ${INSTANCE} --scopes "storage-rw"

# Verify that instance exists
gcloud compute instances describe ${INSTANCE}

# Create a non-root persistent disk to hold your tar file. You can detach and delete the disk afterwards.
gcloud compute disks create ${INSTANCE}-export
gcloud compute instances attach-disk ${INSTANCE} --disk ${INSTANCE}-export --device-name export-disk

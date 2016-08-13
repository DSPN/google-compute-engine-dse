#!/usr/bin/env bash

INSTANCE=instance-2

# You're going to want to ensure this image is built with the latest 14.04.  To check what that is, run:
gcloud compute images list
IMAGE_NAME=ubuntu-1404-trusty-v20160627

# create an instance with that image
# There's some debate about optimal disk size.  We're going with 10GB for now.
gcloud compute --project "datastax-dev" instances create ${INSTANCE} --zone "us-central1-f" --machine-type "n1-standard-8" --network "default" --maintenance-policy "MIGRATE" --scopes default="https://www.googleapis.com/auth/cloud-platform" --image "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/${IMAGE_NAME}" --boot-disk-size "10" --boot-disk-type "pd-standard" --boot-disk-device-name ${INSTANCE} --scopes "storage-rw"

# Verify that instance exists
gcloud compute instances describe ${INSTANCE}

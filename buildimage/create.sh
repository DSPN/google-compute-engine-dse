#!/usr/bin/env bash

# ubuntu-1804-bionic-v20200529                          ubuntu-os-cloud    ubuntu-1804-lts
INSTANCE=datastax-enterprise-ubuntu-1804-bionic-v20200529

# You're going to want to ensure this image is built with the latest 16.04.  To check what that is, run:
gcloud compute images list
IMAGE_NAME=ubuntu-1804-bionic-v20200529

# create an instance with that image
gcloud compute --project "datastax-public" instances create ${INSTANCE} --zone "europe-west2-b" --machine-type "n1-standard-8" --network "default" --maintenance-policy "MIGRATE" --scopes default="https://www.googleapis.com/auth/cloud-platform" --image "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/${IMAGE_NAME}" --boot-disk-size "20" --boot-disk-type "pd-standard" --boot-disk-device-name ${INSTANCE} --scopes "storage-rw"

# Verify that instance exists
gcloud compute instances describe ${INSTANCE} --zone "europe-west2-b"

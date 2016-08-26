#!/usr/bin/env bash

### gcloud commands to copy the disk from our dev project to our public project


#### 1.
# Create a disk from the existing image (datastax-ubuntu-1404-trusty-v20160808) in dev project.
# gcloud compute disks create DISK_NAME --image IMAGE_FROM_DEV_PROJECT --image-project DEV_PROJECT_NAME --project PROD_PROJECT --size 50  --zone us-central1-a
gcloud compute disks create newimagedisk --image datastax-ubuntu-1404-trusty-v20160808 --image-project datastax-dev --project datastax-public --size 20  --zone us-central1-a

#### 2.
# Create an image in public project using the newly created disk
# gcloud compute images create --project PROD_PROJECT --source-disk DISK_NAME --source-disk-zone us-central1-a --description IMAGE_DESCRIPTION
gcloud compute images create datastax-ubuntu-1404-trusty-v20160808 --project datastax-public --source-disk newimagedisk --source-disk-zone us-central1-a --description datastax

#### 3.
# Delete the disk
#​ gcloud compute disks delete NEW_IMAGE_DISK --zone us-central1-a
gcloud compute disks delete newimagedisk --zone us-central1-a --project datastax-public
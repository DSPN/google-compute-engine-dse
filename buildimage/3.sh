#!/usr/bin/env bash

### gcloud commands to copy the disk from our dev project to our public project


#### 1.

# seems this isn't the right way
# Create a disk from the existing image (datastax-ubuntu-1404-trusty-v20160808) in dev project.
# gcloud compute disks create NEW_IMAGE_DISK --image-project DEV_PROJECT --image SOURCE_IMAGE --zone us-central1-a
#gcloud compute disks create newimagedisk --image-project datastax-dev --image datastax-ubuntu-1404-trusty-v20160808 --zone us-central1-a

# new command from Ravi
#gcloud compute disks create DISK_NAME --image IMAGE_FROM_DEV_PROJECT --image-project DEV_PROJECT_NAME --project PROD_PROJECT --size 50  --zone us-central1-a
gcloud compute disks create DISK_NAME --image IMAGE_FROM_DEV_PROJECT --image-project DEV_PROJECT_NAME --project PROD_PROJECT --size 50  --zone us-central1-a

#### 2.

# seems this isn't the right way
# Create an image in public project using the newly created disk
# gcloud compute images create --project PUBLIC_PROJECT  NEW_IMAGE --source-disk NEW_IMAGE_DISK --source-disk-zone us-central1-a
#gcloud compute images create --project datastax-public  datastax-ubuntu-1404-trusty-v20160808 --source-disk newimagedisk --source-disk-zone us-central1-a

# new command from Ravi
#gcloud compute images create --project PROD_PROJECT --source-disk DISK_NAME --source-disk-zone us-central1-a --description IMAGE_DESCRIPTION
gcloud compute images create --project PROD_PROJECT --source-disk DISK_NAME --source-disk-zone us-central1-a --description IMAGE_DESCRIPTION

# 3. Delete the disk
#​ gcloud compute disks delete NEW_IMAGE_DISK --zone us-central1-a
​gcloud compute disks delete newimagedisk --zone us-central1-a

#!/usr/bin/env bash

### gcloud commands to copy the disk from our dev project to our public project

# 1. Create a disk from the existing image (datastax-ubuntu-1404-trusty-v20160808) in dev project.
# gcloud compute disks create NEW_IMAGE_DISK --image-project DEV_PROJECT --image SOURCE_IMAGE --zone us-central1-a
gcloud compute disks create NEW_IMAGE_DISK --image-project datastax-dev --image datastax-ubuntu-1404-trusty-v20160808 --zone us-central1-a

# 2. Create an image in public project using the newly created disk
# gcloud compute images create --project PUBLIC_PROJECT  NEW_IMAGE --source-disk NEW_IMAGE_DISK --source-disk-zone us-central1-a
gcloud compute images create --project datastax-pub  datastax-ubuntu-1404-trusty-v20160808 --source-disk NEW_IMAGE_DISK --source-disk-zone us-central1-a

# 3. Delete the disk
#​ gcloud compute disks delete NEW_IMAGE_DISK --zone us-central1-a
​gcloud compute disks delete NEW_IMAGE_DISK --zone us-central1-a

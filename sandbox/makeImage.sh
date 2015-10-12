#!/bin/sh

ZONE="us-central1-f"
INSTANCE="datastax-enterprise"
PROJECT_ID="datastax-dev"
IMAGE_DESCRIPTION="DataStax"
BUCKET_NAME="datastax"
VM_INSTANCE_NAME="myinstance"

#gcloud compute instances describe $INSTANCE --project $PROJECT_ID --zone $ZONE
#gcloud compute disks create ${INSTANCE}-export2 --project ${PROJECT_ID} --zone ${ZONE}
#gcloud compute instances attach-disk ${INSTANCE} --disk ${INSTANCE}-export2 --device-name export-disk --project ${PROJECT_ID} --zone ${ZONE}
#gcloud compute ssh ${INSTANCE} --project ${PROJECT_ID} --zone ${ZONE}
#gcloud compute instances delete ${INSTANCE} --project ${PROJECT_ID}  --zone ${ZONE} --keep-disks all
#gcloud compute --project ${PROJECT_ID} instances create ${INSTANCE} --zone ${ZONE} --scopes "storage-rw" --disk "name=${INSTANCE}" "device-name=${INSTANCE}" "mode=rw" "boot=yes"
#gcloud compute --project ${PROJECT_ID} images create ${INSTANCE}-image --description ${IMAGE_DESCRIPTION} --source-uri https://storage.googleapis.com/${BUCKET_NAME}/${INSTANCE}-image-licensed.tar.gz

gcloud config set project $PROJECT_ID
gcloud compute instances create ${VM_INSTANCE_NAME} --image ${INSTANCE}-image  

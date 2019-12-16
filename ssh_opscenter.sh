#!/bin/bash

gcloud compute ssh --ssh-flag=-L8443:localhost:8443 \
--project=$gcp_project \
--zone=`gcloud compute instances list \
--project $gcp_project | grep ${deployment_name}-opscenter-vm \
| awk '{print $2}'` ${deployment_name}-opscenter-vm


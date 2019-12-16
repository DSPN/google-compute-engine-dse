#!/bin/sh

gcloud deployment-manager deployments create $deployment_name \
--config clusterParameters.yaml \
--project $gcp_project

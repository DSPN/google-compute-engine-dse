#!/bin/sh

DEPLOYMENT_NAME=$1
gcloud deployment-manager deployments create $DEPLOYMENT_NAME --config casssandra.yaml

#!/usr/bin/env bash

# SSH into the instance
INSTANCE=instance-11
gcloud compute ssh ${INSTANCE}

sudo bash

### Do nothing

# Halt the machine so the Google people can take the image
sudo shutdown -h now

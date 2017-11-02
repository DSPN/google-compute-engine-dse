### Procedure to create custom Ubuntu image for DataStax Enteprise Google Launcher solution based on Google's stock image: ubuntu-1404-trusty-v20171026

*Run % gcloud init (make sure to use datastax-public project)
*Run % git clone https://github.com/DSPN/google-compute-engine-dse
*Run % cd google-compute-engine-dse/buildimage
*Update 1.sh file to reflect your new Google's stock Ubuntu image
*Run % ./1.sh
*Continue from step 5 through step 9 in [here](https://cloud.google.com/launcher/docs/partners/technical-components)
*Update build_image.sh to reflect your new Google's stock Ubuntu image
*Run % ./build_image.sh


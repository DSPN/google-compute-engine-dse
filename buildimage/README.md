### Procedure to create custom Ubuntu image for DataStax Enterprise Google Launcher solution using Google's stock image: (ubuntu-1404-trusty-v20180110)

* Run % gcloud init (make sure to use datastax-public project)
* Run % git clone https://github.com/DSPN/google-compute-engine-dse
* Run % cd google-compute-engine-dse/buildimage
* Review and update 1.sh and build_image.sh to reflect your new Google's stock Ubuntu image
    * IMAGE_NAME should be the latest stock image - use gcloud compute images list | grep ubuntu-1604 to find latest
    * INSTANCE is the name we want to call it - something like instance-ubuntu-1604-xenial-v20181011-tb
* Run % ./1.sh
* If you need to add extra packages or other software, it should be done now. ssh into VM and perfrom these activities
* Continue from step 5 through step 9 in [here](https://cloud.google.com/launcher/docs/partners/technical-components)
   * Clean up your disk.
* Run % gcloud auth application-default login (ensure to authenticate against the datastax-public project through setting the environment variable: GOOGLE_APPLICATION_CREDENTIALS)
* Run % ./build_image.sh - first update the disk image with the one you just created


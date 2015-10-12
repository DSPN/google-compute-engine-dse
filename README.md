# google-cloud-platform-dse

The deploy.sh script will run this GCP template.  Currently it deploys nodes and installs OpsCenter.

To do items include:
* Test with hostnames, use IPs if that doesn't work
* Ensure dependencies are complete before OpsCenter provision starts
* Currently we are using SSD persistent disks (pd-ssd).  We may want to move to ephemeral ssd (local-ssd).  In that case, we would provide options for 1,2,3 or 4 disks.

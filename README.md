# google-cloud-platform-dse

The deploy.sh script will run this GCP template.  Currently it deploys nodes and installs OpsCenter.

To do items include:
* Propagate SSH keys so OpsCenter can use them
* Ensure dependencies are complete before OpsCenter provision starts
* Test with hostnames, use IPs if that doesn't work
* Use local ssds, providing option for 1, 2, 3 or 4

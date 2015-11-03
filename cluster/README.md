# cluster

The deploy.sh script will run this GCP template.  It deploys nodes in the specified zones, installs OpsCenter and then provisions those nodes with DataStax Enterprise.  Upon completion, the cluster can be viewed in OpsCenter by accessing the public IP of the OpsCenter node on port 8888.
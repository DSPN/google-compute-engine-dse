# google-compute-engine-dse

This is a Google Deployment Manager template for Google Compute Engine (GCE) that will deploy a single or multiple datacenter cluster.  deploy.sh is the main entry point.  The clusterParameters.* files give some example configurations.

The [DataStax Enterprise Deployment Guide for Google](https://academy.datastax.com/resources/deployment-guide-google) provides background on best practices in Google Cloud Platform (GCP) as well as instructions on using Google Cloud Launcher.  Cloud Launcher is Google's graphical tool for creating deployments.  This template is used in our Cloud Launcher deployment.

# Deploying to Google Cloud Platform (GCP)

## Set up GCP Prerequisites

To use these templates, you will need to register for a GCP account.  Google offers a free trial for new users.  You will also need to install the Cloud SDK locally or use the Google Cloud Shell.  In these instruction we use a local install of the Cloud SDK.  More information is available at:
* https://cloud.google.com/sdk/
* https://cloud.google.com/shell/docs/

If you haven't already, you will also need to create a GCP project.  That can be accomplished in the Google Cloud Console here: https://console.cloud.google.com/ 

After creating the project, set it as the default project that gcloud will use with the command:

    gcloud config set project myproject

## Clone the Template Repo

Now that you have the gcloud tools installed, you’ll want to clone of copy of the template repo.  The GCE repo is here: https://github.com/DSPN/google-compute-engine-dse

To clone it use the command:

    git clone https://github.com/DSPN/google-compute-engine-dse.git

If all went well, output should look something like this:



Now cd into the repo dir and list files there using the commands:

cd google-cloud-platform-dse
ls


Our main entry point is a file called deploy.sh. We can inspect that file using the commands:

clear
cat deploy.sh


This is an extremely simple shell script that invokes the Google Cloud SDK. It takes one argument, the name of the deployment. The deployment name needs to be unique within you project. The deploy.sh script also depends on the input file clusterParameters.yaml. This file defines our cluster topology. Let’s take a quick look with the following commands:

clear
cat clusterParameters.yaml


This config is going to create 3 nodes in each of 3 different regions, for a total of 9 nodes. Each node is a very small machine, an n1-standard-1. This isn’t a size we’d recommend for production use but is fine for testing out a deployment. Similarly, each node will be configured with a 10GB pd-ssd. This is an extremely small disk for a production environment but will be fine for our test deployment.

Two example config files are provided, clusterParameters.small.yaml and clusterParameters.large.yaml. The large one creates nodes in every Google zone currently available. You may need to request you core quotas be increased to run it.

We encourage you to look at the templates more and better understand what they’re doing. They are provided to get you started and we fully expect you to customize them in ways that suit your needs.

Now that we’ve had a look through the project, let’s try running it!

2.6 Create a Deployment

We’re going to start of by creating a new deployment. I’m going to call mine ben1. To create it, I’m going to enter the command:

./deploy.sh ben1
When I do that, I see the following output:



At this point, the physical resources on GCE have all provisioned. However, each machine has a script that runs and installs Java as well as provisioning DSE. That will take another few minutes to run.

2.7 Inspecting the Output

The easiest way to inspect output is in the web interface. You can access this at http://cloud.google.com.  Once logged in, click on "my console." If you click the three horizontal lines in the upper left and scroll down, you should see an option under "Tools" titled "Deployment Manager." Click that.



Now, click on your deployment and view the tree describing it:



The ben1-opscenter-vm is the machine running our instance of OpsCenter. I’m going to click select that and click "Manage Resource."



Scrolling down, I see the external ip for the OpsCenter machine. Enter that IP into your url bar and add ":8888" to access OpsCenter on port 8888. If you do this relatively quickly after deployment, all nodes might not yet be available.  It's also possible you will see an error stating agents can't connect as shown below.  Dismiss that.  To resolve it permanently, you may need to ssh into the opscenter box and run the command:

sudo service restart opscenterd


If the cluster build completes successfully, you should see the following if you used clusterParameters.small.yaml as input:

Clicking on the nodes button, we can now see a graphical view of the cluster topology:



At this point you have a running DSE cluster! You can ssh into any of the nodes using Google ssh console and begin working with DSE.  The OpsCenter node does not run DSE, only the OpsCenter administrator interface.  To do that click on any of the nodes in the Google Console and click ssh.  A window will open showing an SSH console.  Interesting commands to get your started include:

nodetool status
cqlsh


2.8 Deleting a Deployment

Deployments can be deleted via the command line or the web UI. To use the command line type the command:

gcloud deployment-manager deployments delete ben1

Running from the command line, I see the following output;



To delete the deployment in the web UI, click the trash can icon on the "Deployment Manager" page as show below:



3 Conclusion

This document covers the basics of getting up and running with DataStax Enterprise in GCP.  If you have questions or comments please direct those to ben.lackey@datastax.com or @benofben.
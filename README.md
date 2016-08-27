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

## Clone and Investigate the Template Repo

Now that you have the gcloud tools installed, you’ll want to clone of copy of the template repo.  The GCE repo is here: https://github.com/DSPN/google-compute-engine-dse

To clone it use the command:

    git clone https://github.com/DSPN/google-compute-engine-dse.git

If all went well, output should look something like this:

![](./img/gitclone.png)

Now cd into the repo dir and list files there using the commands:

    clear
    cd google-compute-engine-dse
    ls

![](./img/ls.png)

Our main entry point is a file called deploy.sh. We can inspect that file using the commands:

    clear
    cat deploy.sh

![](./img/catdeploy.png)

This is an extremely simple shell script that invokes the Google Cloud SDK. It takes one argument, the name of the deployment. The deployment name needs to be unique within you project. The deploy.sh script also depends on the input file clusterParameters.yaml. This file defines our cluster topology. Let’s take a quick look with the following commands:

    clear
    cat clusterParameters.yaml

![](./img/catclusterparameters.png)

This config is going to create 3 nodes in each of 3 different regions, for a total of 9 nodes. Each node is a very small machine, an n1-standard-2. This isn’t a size we’d recommend for production use but is fine for testing out a deployment. Similarly, each node will be configured with a 20GB pd-ssd.  This is an extremely small disk but will be sufficient for our test deployment.

Two example config files are provided, clusterParameters.small.yaml and clusterParameters.large.yaml. The large one creates nodes in every Google zone currently available. You may need to request you core quotas be increased to run it.

We encourage you to look at the templates more and better understand what they’re doing. They are provided to get you started and we fully expect you to customize them in ways that suit your needs.

Now that we’ve had a look through the project, let’s try running it!

## Create a Deployment

We’re going to start of by creating a new deployment. I’m going to call mine ben1. To create it, I’m going to enter the command:

    clear
    ./deploy.sh ben1

When I do that, I see the following output:

![](./img/deploy.png)

At this point, the physical resources on GCE have all provisioned. However, each machine has a script that runs and installs Java as well as provisioning DSE. That will take another few minutes to run.

## Inspecting the Deployment

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

## Inspecting the Cluster

The infrastructure will take a few minutes to deploy.  When complete you should see:

![](./img/deployed.png)

To view OpsCenter, the DataStax admin interface, we will need to create an ssh tunnel.  To do that, open a terminal on your local machine and run the command:

    gcloud compute ssh --ssh-flag=-L8888:localhost:8888 --project=<NAME OF YOUR PROJECT> --zone=us-central1-f datastax-enterprise-1-opscenter-vm 

In my case, the project is named datastax-dev, though it will have a different name for you.

![](./img/tunnel.png)

Now, we can open a web browser to http://localhost:8888 to view OpsCenter.

![](./img/opscenter.png)

Great!  You now have a DataStax Enterprise cluster running with 3 nodes in Asia, Europe and America.

We can also log into a node to interact with the database.  To do that go back to the Google console.

![](./img/nodes.png)

Click on any node.  In DataStax Enterprise the nodes are homogeneous so we can interact with any one.

![](./img/node.png)

We can connect to that node by clicking "SSH."  This will open an SSH window.

![](./img/terminal.png)

At this point we can clear the terminal window and start up cqlsh, the command line interface to DataStax Enterprise.

    clear
    cqlsh

![](./img/cqlsh.png)

From there you can issue any valid cql command.  For instance:

    desc keyspace
    
![](./img/desc.png)
    
## Deleting a Deployment

Deployments can be deleted via the command line or the web UI. To use the command line type the command:

    gcloud deployment-manager deployments delete ben1

## Next Steps

If you want to learn more about DataStax Enterprise, the online training courses at https://academy.datastax.com/ are a great place to start.

To learn more about running DataStax Enterprise on GCP take a look at the [bestpractices guide](bestpractices.md) and [post deploy steps](postdeploy.md).
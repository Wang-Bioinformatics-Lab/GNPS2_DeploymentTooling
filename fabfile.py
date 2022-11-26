from fabric2 import Connection
from fabric2 import task
from fabric2 import config
import os
import time
import uuid
import glob
import json
import urllib.parse
import io
import yaml


@task
def deploy_workflow(c, path_to_workflow):
    # Setting the paths
    workflow_input_filename = os.path.join(path_to_workflow, "workflowinput.yaml")
    workflow_display_filename = os.path.join(path_to_workflow, "workflowdisplay.yaml")

    # Validate Input
    try:
        workflow_input_specifications = yaml.safe_load(open(workflow_input_filename))
    except:
        print("Cannot Parse Workflow Input File")
        raise

    workflow_name = workflow_input_specifications["workflowname"]

    # Validate display
    try:
        workflow_display_specifications = yaml.safe_load(open(workflow_display_filename))
    except:
        print("Cannot Parse Workflow Display File")
        raise
    assert(workflow_name == workflow_display_specifications["name"])

    # Doing stuff
    print(workflow_display_specifications)


    # Making this target folder where we put the actual workflow
    target_workflow_folder = os.path.join(c["paths"]["workflows"], workflow_name)

    nf_workflow_file = os.path.basename(workflow_input_specifications["workflowfile"])

    print(workflow_input_specifications)

    # Now we will determine what to copy over
    files_to_copy = ["workflowinput.yaml", "workflowdisplay.yaml", nf_workflow_file]
    print(c["paths"]["workflows"])
    
    
    

from fabric2 import Connection
from fabric2 import task
from fabric2 import config
from patchwork.files import exists
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

    workflow_name = os.path.basename(workflow_input_specifications["workflowname"])

    # Validate display
    try:
        workflow_display_specifications = yaml.safe_load(open(workflow_display_filename))
    except:
        print("Cannot Parse Workflow Display File")
        raise

    assert(workflow_name == workflow_display_specifications["name"])

    # Printing
    #print(json.dumps(workflow_display_specifications, indent=4))

    # Making this target folder where we put the actual workflow
    target_workflow_folder = os.path.join(c["paths"]["workflows"], workflow_name)

    nf_workflow_file = os.path.basename(workflow_input_specifications["workflowfile"])

    #print(workflow_input_specifications)

    # Prepping workflow on the remote side
    if exists(c, target_workflow_folder):
        print("Workflow {} Exists on Remote Server".format(workflow_name))
        input_val = input('Continue y/n: ')
        if input_val != "y":
            exit(0)
    else:
        print("Workflow {} Does not exist on Remote Server".format(workflow_name))
        input_val = input('Continue y/n: ')
        if input_val != "y":
            exit(0)
    
    c.run("mkdir -p {}".format(target_workflow_folder))

    # Now we will determine what to copy over
    files_to_copy = ["workflowinput.yaml", "workflowdisplay.yaml", nf_workflow_file, "bin"]

    REMOTE_WORKFLOW_DIR = c["paths"]["workflows"]

    for filename in files_to_copy:
        local_file = os.path.join(path_to_workflow, filename)
        remote_file = os.path.join(REMOTE_WORKFLOW_DIR, workflow_name, filename)
        if os.path.isdir(local_file):
            update_folder(c, local_file, remote_file)
            update_permissions(c, remote_file, "777")
            print("Copying Folder ", local_file, " to ", remote_file)
        else:
            update_file(c, local_file, remote_file)
            update_permissions(c, remote_file, "777")
            print("Copying File ", local_file, " to ", remote_file)
        
    #print(c["paths"]["workflows"])

# Utility function to update a single file
def update_file(c, local_path, final_path, ):
    try:
        c.put(local_path, final_path, preserve_mode=True)
    except:
        c.put(local_path, final_path, preserve_mode=False)

def update_permissions(c, remote_file, permissions):
    # This is to run chmod on the file
    c.run("chmod -R {} {}".format(permissions, remote_file))

# Utility function to update an entire folder
def update_folder(c, local_path, final_path):
    # Tar up local folder and upload to temporary space on server and untar
    local_temp_path = os.path.join("/tmp/{}_{}.tar".format(local_path.replace("/", "_"), str(uuid.uuid4())))
    cmd = "tar -C {} -chf {} .".format(local_path, local_temp_path)
    # print(cmd)
    os.system(cmd)

    remote_temp_tar_path = os.path.join("/tmp/{}_{}.tar".format(local_path.replace("/", "_"), str(uuid.uuid4())))
    c.put(local_temp_path, remote_temp_tar_path, preserve_mode=True)

    remote_temp_path = os.path.join("/tmp/{}_{}".format(local_path.replace("/", "_"), str(uuid.uuid4())))
    c.run("mkdir {}".format(remote_temp_path))
    c.run("tar -C {} -xf {}".format(remote_temp_path, remote_temp_tar_path))

    c.run('rsync -rlptD {}/ {}'.format(remote_temp_path, final_path))

    if os.path.split(os.path.normpath(remote_temp_path))[0] == '/tmp':
        c.run('rm -rf {}'.format(remote_temp_path))
    if os.path.split(os.path.normpath(remote_temp_tar_path))[0] == '/tmp':
        c.run('rm {}'.format(remote_temp_tar_path))
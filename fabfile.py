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

@task
def deploy_workflow(c, workflow_input_filename):
    print("XXX")


import subprocess
import os
import sys
import shutil
from pathlib import Path


def init_checks():
    """
    Perform general checks,
    Check compatible python version,
    existence of 'config.local' file
    executable 'kubectl' command
    executable 'helm' command

    :return:
    """
    # Make sure python 3.5 and above is used
    if sys.version_info[0] < 3 or sys.version_info[1] < 5:
        print("Python 3.5 is a minimal requirement")
        exit(1)

    # Make sure config.local exists
    config_file = Path(str(Path.home()) + "/.kube/config.local")
    if not config_file.exists():
        print("Could not locate {}\nMake sure to create it".format(config_file))
        exit(1)

    os.environ["KUBECONFIG"] = str(config_file)

    # Make sure kubectl command exists
    if shutil.which("kubectl") is None:
        print("Could not execute 'kubectl' command\nMake sure 'kubectl' installed")
        exit(1)

    # .run return CompletedProcess with returncode and stdout and stderr values as bytes object, using UTF-8 decode
    cluster_info_output = subprocess.run(["kubectl", "cluster-info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # In case returncode is not 0
    if cluster_info_output.returncode:
        print(cluster_info_output.stderr.decode('utf-8') +
              "Make sure your cluster is up and running, and config file contains correct values")
        exit(1)
    # else:
    #     print(cluster_info_output.stdout.decode('utf-8'))

    # Make sure helm command exists
    if shutil.which("helm") is None:
        print("Could not execute 'helm' command,\n"
              "Make sure 'helm' installed: https://docs.helm.sh/using_helm/#installing-helm")
        exit(1)

    helm_init_output = subprocess.run(["helm", "init"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # In case returncode is not 0
    if helm_init_output.returncode:
        print(helm_init_output.stderr.decode('utf-8'))
        exit(1)
    # else:
    #     print(helm_init_output.stdout.decode('utf-8'))

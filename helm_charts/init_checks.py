
import os
import sys
import shutil
from pathlib import Path
from subprocess import run, PIPE


def init_checks(config_file, cluster_context, execute_helm_init=False):
    """
    Perform general checks,
    Check compatible python version,
    executable 'kubectl' command
    export current config_file as environment variable (KUBECONFIG)
    setup cluster context
    existence of 'config_local' file
    executable 'helm' command

    :param config_file: String
    :param cluster_context: String
    :param execute_helm_init: Boolean
    :return:
    """
    # Make sure python 3.5 and above is used
    if sys.version_info[0] < 3 or sys.version_info[1] < 5:
        print("Python 3.5 is a minimal requirement")
        exit(1)

    # Make sure config_file exists
    if not Path(config_file).exists():
        print("Could not locate {}\nMake sure to create it".format(config_file))
        exit(1)

    # Make sure kubectl command exists
    if shutil.which("kubectl") is None:
        print("Could not execute 'kubectl' command\nMake sure 'kubectl' installed")
        exit(1)

    # Export config_file since the user may exported other file on same terminal process
    os.environ["KUBECONFIG"] = str(config_file)

    print("Config file used: {}\n"
          "Context used: {}".format(config_file, cluster_context))
    use_context_output = run(["kubectl", "config", "--kubeconfig", config_file,
                              "use-context", cluster_context], stdout=PIPE, stderr=PIPE)
    # In case returncode is not 0
    if use_context_output.returncode:
        print(use_context_output.stderr.decode('utf-8') +
              "Make sure your cluster is up and running, "
              "and '{}' file contains correct values".format(config_file))
        exit(1)

    # .run return CompletedProcess with returncode and stdout and stderr values as bytes object, using UTF-8 decode
    print("Retrieving cluster information")
    cluster_info_output = run(["kubectl", "cluster-info"], stdout=PIPE, stderr=PIPE)

    # In case returncode is not 0
    if cluster_info_output.returncode:
        print(cluster_info_output.stderr.decode('utf-8') +
              "Make sure your cluster is up and running, "
              "and '{}' file contains correct values".format(config_file))
        exit(1)
    # else:
    #     print(cluster_info_output.stdout.decode('utf-
    # Make sure helm command exists
    if shutil.which("helm") is None:
        print("Could not execute 'helm' command,\n"
              "Make sure 'helm' installed: https://docs.helm.sh/using_helm/#installing-helm")
        exit(1)

    helm_version_output = run(["helm", "version"], stdout=PIPE, stderr=PIPE)
    if helm_version_output.returncode:
        print(helm_version_output.stderr.decode('utf-8') +
              "Please fix helm first, consider executing this app with --helm-init flag")
        exit(1)

    if execute_helm_init:
        print("Executing 'helm init' command")
        helm_init_output = run(["helm", "init"], stdout=PIPE, stderr=PIPE)
        # In case returncode is not 0
        if helm_init_output.returncode:
            print(helm_init_output.stderr.decode('utf-8'))
            exit(1)
    # else:
    #     print(helm_init_output.stdout.decode('utf-8'))

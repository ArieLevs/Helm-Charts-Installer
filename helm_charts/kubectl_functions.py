
from subprocess import run, PIPE


def get_cluster_info():
    """
    Get cluster information

    :return: return value from command execution as string
    """
    cluster_info_completed_process = run(["kubectl", "cluster-info"], stdout=PIPE, stderr=PIPE)

    if cluster_info_completed_process.returncode == 0:
        return cluster_info_completed_process.stdout.decode('utf-8').strip()
    else:
        return cluster_info_completed_process.stderr.decode('utf-8').strip()


def create_registry_secret(secret_name, docker_registry, docker_username, docker_password, namespace):
    """
    Create a new docker-registry secret

    :param secret_name: String
    :param docker_registry: String
    :param docker_username: String
    :param docker_password: String
    :param namespace: String
    :return: return code and value from command execution as dictionary
    """
    add_registry_completed = run(["kubectl", "create", "secret", "docker-registry", secret_name,
                                             "--docker-server=%s" % docker_registry,
                                             "--docker-username=%s" % docker_username,
                                             "--docker-password=%s" % docker_password,
                                             "--namespace=%s" % namespace],
                                 stdout=PIPE,
                                 stderr=PIPE)
    if add_registry_completed.returncode == 0:
        value = add_registry_completed.stdout.decode('utf-8').strip()
    else:
        value = add_registry_completed.stderr.decode('utf-8').strip()

    return {'returncode': add_registry_completed.returncode, 'value': value}


def identify_cluster_namespaces():
    """
    Execute 'kubectl get namespaces' command and return dict with status and value as decoded (utf-8) string

    'kubectl get namespaces' command return example:
    NAME              STATUS    AGE
    default           Active    6d
    docker            Active    6d
    ingress-traefik   Active    5d4h
    kube-public       Active    6d
    kube-system       Active    6d

    :return: return code and value from execution command decoded string
    """
    # Execute 'kubectl get namespaces' command, returned as CompletedProcess
    namespaces_completed_process = run(["kubectl", "get", "namespaces"], stdout=PIPE, stderr=PIPE)

    status = namespaces_completed_process.returncode
    # If return code is not 0
    if status:
        return {'status': status, 'value': namespaces_completed_process.stderr.decode('utf-8').strip()}
    else:
        return {'status': status, 'value': namespaces_completed_process.stdout.decode('utf-8').strip()}


def parse_cluster_namespaces_output(get_namespaces_output):
    """
    Function will perform a manipulation on a string output from the 'kubectl get namespaces' command

    Returns an array of dicts with installed repos names and urls as strings
    as [{'name': 'some_namespace', 'status': 'active', 'age': '5h20m'}]

    by validating the first line, splitting by the tab delimiter,
    and checking that the first (0) value is 'NAME' second (1) value is 'STATUS' and third (2) is 'AGE'
    an exception will be raised if the structure was change by kubectl developers

    :param get_namespaces_output: 'kubectl get namespaces' output as String
    :return:
    """
    available_namespaces = []

    # split get_namespaces_output by 'new line'
    get_namespaces_stdout = get_namespaces_output.split("\n")
    # Perform validation on stdout of first (0) line
    first_line_stdout = get_namespaces_stdout[0].split()
    if first_line_stdout[0].strip() != 'NAME' or \
            first_line_stdout[1].strip() != 'STATUS' or \
            first_line_stdout[2].strip() != 'AGE':
        raise Exception("'kubectl get namespaces' command output changed, "
                        "code change is needed to resolve this issue, "
                        "contact the developer.")

    # for every line in existing namespaces, excluding the headers line (NAME, STATUS and AGE)
    for line in get_namespaces_stdout[1:]:
        # each stdout 'kubectl get namespaces' line composed by tabs delimiter, split it
        namespace_details = line.split()

        temp_dictionary = {}
        if namespace_details[0] != "":
            # Add current line repo values to dict
            temp_dictionary.update({'name': namespace_details[0].strip()})
            temp_dictionary.update({'status': namespace_details[1].strip()})
            temp_dictionary.update({'age': namespace_details[2].strip()})
            # Update final array with the temp array of dicts of current repo
            available_namespaces.append(temp_dictionary)

    return available_namespaces


import subprocess
import os

values_dir_path = os.path.dirname(os.path.realpath(__file__)) + '/values_files/'

supported_helm_deployments = [
    {'chart_name': 'ingress-traefik',
     'helm_repo_name': 'stable/traefik',
     'name_space': 'ingress-traefik',
     'values_file': values_dir_path + 'ingress-traefik.values.local.yml',
     'private_image': False},

    {'chart_name': 'kubernetes-dashboard',
     'helm_repo_name': 'stable/kubernetes-dashboard',
     'name_space': 'kube-system',
     'values_file': values_dir_path + 'kubernetes-dashboard.values.local.yml',
     'private_image': False},

    {'chart_name': 'jenkins',
     'helm_repo_name': 'stable/jenkins',
     'name_space': 'jenkins',
     'values_file': values_dir_path + 'jenkins.values.local.yml',
     'private_image': False},

    {'chart_name': 'nalkinscloud-nginx',
     'helm_repo_name': 'nalkinscloud/nalkinscloud-nginx',
     'name_space': 'nalkinscloud-nginx',
     'values_file': values_dir_path + 'nalkinscloud-nginx.values.local.yml',
     'private_image': False},

    {'chart_name': 'nalkinscloud-frontend',
     'helm_repo_name': 'nalkinscloud/nalkinscloud',
     'name_space': 'nalkinscloud-frontend',
     'values_file': values_dir_path + 'nalkinscloud.frontend.values.local.yml',
     'private_image': True},

    {'chart_name': 'nalkinscloud-api',
     'helm_repo_name': 'nalkinscloud/nalkinscloud',
     'name_space': 'nalkinscloud-api',
     'values_file': values_dir_path + 'nalkinscloud.api.values.local.yml',
     'private_image': True},
]


def identify_installed_helm_repos(return_only_decoded_string=False):
    """
    Function will perform a manipulation on a string output from the 'helm repo list' command
    If 'return_only_decoded_string' True, do not perform any string processing

    Returns an array of dicts with installed repos names and urls as strings
    as [{'repo_name': 'some_repo_name', 'repo_url': 'some_repo_url'}]

    'helm repo list' command return example:
    NAME        	URL
    stable      	https://kubernetes-charts.storage.googleapis.com
    local       	http://127.0.0.1:8879/charts
    nalkinscloud	https://arielevs.github.io/Kubernetes-Helm-Charts/

    by validating the first line, splitting by the tab delimiter,
    and checking that the first (0) value is 'NAME' and second (1) value is 'URL'
    an exception will be raised if the structure was change by HELM developers

    :param return_only_decoded_string: if True then return decoded (utf-8) "original" 'helm repo list' command output
    :return: array of dicts with repo installations
    """
    # Execute 'helm list' command, returned as CompletedProcess
    installed_repos_completed_process = subprocess.run(["helm", "repo", "list"],
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE)

    if return_only_decoded_string:
        if installed_repos_completed_process.returncode == 0:
            value = installed_repos_completed_process.stdout.decode('utf-8').strip()
        else:
            value = installed_repos_completed_process.stderr.decode('utf-8').strip()
        return value

    installed_repos = []

    # In case returncode is 0
    if not installed_repos_completed_process.returncode:
        # get stdout from installed_repos_completed_process, and decode for 'utf-8'
        # split stdout of installed_repos_completed_process by 'new line'
        installed_repos_stdout = installed_repos_completed_process.stdout.decode('utf-8').split("\n")

        # Perform validation on stdout of first (0) line
        first_line_stdout = installed_repos_stdout[0].split("\t")
        if first_line_stdout[0].strip() != 'NAME' or first_line_stdout[1].strip() != 'URL':
            raise Exception("'helm repo list' command output changed, "
                            "code change is needed to resolve this issue, "
                            "contact the developer.")

        # for every line in installed repos, excluding the headers line (NAME and URL)
        for line in installed_repos_stdout[1:]:
            # each stdout 'helm repo list' line composed by tabs delimiter, split it
            repo_details = line.split("\t")

            temp_dictionary = {}
            if repo_details[0] != "":
                # Add current line repo values to dict
                temp_dictionary.update({'repo_name': repo_details[0].strip()})
                temp_dictionary.update({'repo_url': repo_details[1].strip()})
                # Update final array with the temp array of dicts of current repo
                installed_repos.append(temp_dictionary)

    return installed_repos


def add_helm_repo(repo_name, repo_url):
    """
    Execute 'helm repo add' command on input values

    :param repo_name: name of repository as strings
    :param repo_url: url of repository as string
    :return: return code and value from execution command as dict
    """
    # execute and get CompletedProcess object
    completed_process_object = subprocess.run(["helm", "repo", "add", repo_name, repo_url],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
    if completed_process_object.returncode == 0:
        value = completed_process_object.stdout.decode('utf-8')
    else:
        value = completed_process_object.stderr.decode('utf-8')
    return {'status': completed_process_object.returncode, 'value': value}


def remove_helm_repo(repos_array):
    """
    Execute 'helm repo remove' command on input values
    repos_array is an array of strings as:
    ['stable', 'local', 'nalkinscloud', ...]

    :param repos_array: array of strings
    :return: return code and value from execution command as dict
    """
    status = 0
    value = 'no errors found'
    for repo in repos_array:
        completed_process_object = subprocess.run(["helm", "repo", "remove", repo],
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
        # In case of a non 0 return code, update return from last iteration
        if completed_process_object.returncode != 0:
            status = completed_process_object.returncode
            value = completed_process_object.stderr.decode('utf-8') + " *** Additional errors may occurred"

    return {'status': status, 'value': value}


def identify_installed_helm_charts(return_only_decoded_string=False):
    """
    Function will perform a manipulation on a string output from the 'helm list' command
    If 'return_only_decoded_string' True, do not perform any string processing

    Returns an array of dicts with installed chart names and namespaces as strings
    as [{'chart_name': 'some_chart_name', 'name_space': 'some_name_space'}]

    'helm list' command return example:
    NAME                	REVISION	UPDATED                 	STATUS  	CHART                     	NAMESPACE
    ingress-traefik     	2       	Thu Dec 27 19:45:01 2018	DEPLOYED	traefik-1.56.0            	ingress-traefik
    kubernetes-dashboard	11      	Sun Sep 16 11:21:24 2018	DEPLOYED	kubernetes-dashboard-0.7.3	kube-system

    by validating the first line, splitting by the tab delimiter,
    and checking that the first (0) value is 'NAME' and sixth (5) value is 'NAMESPACE'
    an exception will be raised if the structure was change by HELM developers

    :param return_only_decoded_string: if True then return decoded (utf-8) "original" 'helm list' command output
    :return: array of dicts with helm installations
    """
    # Execute 'helm list' command, returned as CompletedProcess
    installed_helm_completed_process = subprocess.run(["helm", "list"],
                                                      stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE)

    if return_only_decoded_string:
        if installed_helm_completed_process.returncode == 0:
            value = installed_helm_completed_process.stdout.decode('utf-8').strip()
        else:
            value = installed_helm_completed_process.stderr.decode('utf-8').strip()
        return value

    installed_charts = []

    # In case returncode is 0
    if not installed_helm_completed_process.returncode:
        # get stdout from installed_helm_completed_process, and decode for 'utf-8'
        # split stdout of installed_helm_completed_process by 'new line'
        installed_helm_stdout = installed_helm_completed_process.stdout.decode('utf-8').split("\n")

        # Perform validation on stdout of first (0) line
        first_line_stdout = installed_helm_stdout[0].split("\t")
        if first_line_stdout[0].strip() != 'NAME' or first_line_stdout[5].strip() != 'NAMESPACE':
            raise Exception("'helm list' command output changed, "
                            "code change is needed to resolve this issue, "
                            "contact the developer.")

        # for every line in installed charts, excluding the headers line (Name, Revision, Updated etc...)
        for line in installed_helm_stdout[1:]:
            # each stdout 'helm list' line composed by tabs delimiter, split it
            chart_details = line.split("\t")

            temp_dictionary = {}
            if chart_details[0] != "":
                # Add current line chart values to dict
                temp_dictionary.update({'chart_name': chart_details[0].strip()})
                temp_dictionary.update({'name_space': chart_details[5].strip()})
                # Update final array with the temp array of dicts of current helm deployment
                installed_charts.append(temp_dictionary)

    return installed_charts


def install_helm_charts(charts_array, docker_registry='', docker_username='', docker_password=''):
    """
    Execute 'helm update' command on input values
    charts_array is an array of strings as:
    ['ingress-traefik', 'kubernetes-dashboard', ...]

    installation process will iterate over the 'supported_helm_deployments' variable,
    which contains an array of dicts with all supported helm charts deployments,
    installation process will init only if 'charts_array' has a value that also exists is 'supported_helm_deployments'

    :param charts_array: array of strings
    :param docker_registry: String
    :param docker_username: String
    :param docker_password: String
    :return: return code and value from execution command as dict
    """
    # Update helm repo before installation
    subprocess.run(["helm", "repo", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    status = 0
    value = 'no errors found'
    for deployment in supported_helm_deployments:
        # Only if current chart name exists in the input 'charts_array'
        if deployment['chart_name'] in charts_array:
            # In case the deployment uses images from private repository
            # then install helm chart with setting the docker-registry secret values
            if deployment['private_image']:
                completed_process_object = subprocess.run(["helm", "upgrade", deployment['chart_name'],
                                                           "--install", deployment['helm_repo_name'],
                                                           "--namespace", deployment['name_space'],
                                                           "-f", deployment['values_file'],
                                                           "--set", "secrets.docker.registry=%s" % docker_registry,
                                                           "--set", "secrets.docker.username=%s" % docker_username,
                                                           "--set", "secrets.docker.password=%s" % docker_password],
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE)
            else:
                completed_process_object = subprocess.run(["helm", "upgrade", deployment['chart_name'],
                                                           "--install", deployment['helm_repo_name'],
                                                           "--namespace", deployment['name_space'],
                                                           "-f", deployment['values_file']],
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE)
            # In case of a non 0 return code, update return from last iteration
            if completed_process_object.returncode != 0:
                status = completed_process_object.returncode
                value = completed_process_object.stderr.decode('utf-8') + " *** Additional errors may occurred"
    return {'status': status, 'value': value}


def delete_helm_installations(charts_array):
    """
    Execute 'helm delete' command on input values
    charts_array is an array of strings as:
    ['ingress-traefik', 'kubernetes-dashboard', ...]

    :param charts_array: array of strings
    :return: return code and value from execution command as dict
    """
    status = 0
    value = 'no errors found'
    for installation in charts_array:
        completed_process_object = subprocess.run(["helm", "delete", "--purge", installation],
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
        # In case of a non 0 return code, update return from last iteration
        if completed_process_object.returncode != 0:
            status = completed_process_object.returncode
            value = completed_process_object.stderr.decode('utf-8') + " *** Additional errors may occurred"
    return {'status': status, 'value': value}


def identify_charts_in_repo(repository_name, return_only_decoded_string=False):
    """
    Execute 'helm repo add' command on input values

    :param repository_name: name of repository as strings
    :param return_only_decoded_string: if True then return decoded (utf-8) "original" 'helm search' command output
    :return: return code and value from execution command as dict
    """
    # execute and get CompletedProcess object
    completed_process_object = subprocess.run(["helm", "search", repository_name],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
    return_code = completed_process_object.returncode
    if return_code != 0:
        return {'status': return_code,
                'value': completed_process_object.stderr.decode('utf-8').strip()}
    else:
        if return_only_decoded_string:
            return {'status': return_code,
                    'value': completed_process_object.stdout.decode('utf-8').strip()}

        # get stdout from completed_process_object, and decode for 'utf-8'
        # split stdout of completed_process_object by 'new line'
        search_repos_stdout = completed_process_object.stdout.decode('utf-8').split("\n")

        # Perform validation on stdout of first (0) line
        first_line_stdout = search_repos_stdout[0].split("\t")
        if first_line_stdout[0].strip() != 'NAME' or first_line_stdout[3].strip() != 'DESCRIPTION':
            raise Exception("'helm search' command output changed, "
                            "code change is needed to resolve this issue, "
                            "contact the developer.")

        charts_list = []
        # for every line in search repo output, excluding the headers line (NAME, CHART VERSION etc)
        for line in search_repos_stdout[1:]:
            # each stdout 'helm search' line composed by tabs delimiter, split it
            chart_details = line.split("\t")

            temp_dictionary = {}
            if chart_details[0] != "":
                # Add current line chart values to dict
                temp_dictionary.update({'chart_name': chart_details[0].strip()})
                temp_dictionary.update({'chart_version': chart_details[1].strip()})
                temp_dictionary.update({'app_version': chart_details[2].strip()})
                temp_dictionary.update({'description': chart_details[3].strip()})
                # Update final array with the temp array of dicts of current charts
                charts_list.append(temp_dictionary)

    return {'status': return_code, 'value': charts_list}

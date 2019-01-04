
import os
from subprocess import run, PIPE


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


def identify_installed_helm_repos():
    """
    Execute 'helm repo list' command and return dict with status and value as decoded (utf-8) string

    'helm repo list' command return example:
    NAME        	URL
    stable      	https://kubernetes-charts.storage.googleapis.com
    local       	http://127.0.0.1:8879/charts
    nalkinscloud	https://arielevs.github.io/Kubernetes-Helm-Charts/

    :return: return code and value from execution command decoded string
    """
    # Execute 'helm list' command, returned as CompletedProcess
    installed_repos_completed_process = run(["helm", "repo", "list"], stdout=PIPE, stderr=PIPE)

    status = installed_repos_completed_process.returncode
    # If return code is not 0
    if status:
        return {'status': status, 'value': installed_repos_completed_process.stderr.decode('utf-8').strip()}
    else:
        return {'status': status, 'value': installed_repos_completed_process.stdout.decode('utf-8').strip()}


def parse_helm_repo_list_output(helm_repo_list_output):
    """
    Function will perform a manipulation on a string output from the 'helm repo list' command

    Returns an array of dicts with installed repos names and urls as strings
    as [{'repo_name': 'some_repo_name', 'repo_url': 'some_repo_url'}]

    by validating the first line, splitting by the tab delimiter,
    and checking that the first (0) value is 'NAME' and second (1) value is 'URL'
    an exception will be raised if the structure was change by HELM developers

    :param helm_repo_list_output: 'helm repo list' output as String
    :return:
    """
    installed_repos = []

    # split helm_repo_list_output by 'new line'
    installed_repos_stdout = helm_repo_list_output.split("\n")

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


def identify_installed_helm_charts():
    """
    Execute 'helm list' command and return dict with status and value as decoded (utf-8) string

    'helm list' command return example:
    NAME                	REVISION	UPDATED                 	STATUS  	CHART                     	APP VERSION     NAMESPACE
    ingress-traefik     	2       	Thu Dec 27 19:45:01 2018	DEPLOYED	traefik-1.56.0            	1.7.6           ingress-traefik
    kubernetes-dashboard	11      	Sun Sep 16 11:21:24 2018	DEPLOYED	kubernetes-dashboard-0.7.3	1.10.1          kube-system

    :return: array of dicts with helm installations
    """
    # Execute 'helm list' command, returned as CompletedProcess
    installed_helm_completed_process = run(["helm", "list"], stdout=PIPE, stderr=PIPE)

    status = installed_helm_completed_process.returncode
    # If return code is not 0
    if status:
        return {'status': status, 'value': installed_helm_completed_process.stderr.decode('utf-8').strip()}
    else:
        return {'status': status, 'value': installed_helm_completed_process.stdout.decode('utf-8').strip()}


def parse_helm_list_output(helm_list_output):
    """
    Function will perform a manipulation on a string output from the 'helm list' command

    Returns an array of dicts with installed chart names and namespaces as strings
    as [{'chart_name': 'some_chart_name', 'name_space': 'some_name_space'}]

    by validating the first line, splitting by the tab delimiter,
    and checking that the first (0) value is 'NAME' and seventh (6) value is 'NAMESPACE'
    an exception will be raised if the structure was change by HELM developers

    :param helm_list_output: 'helm list' output as String
    :return: list of dicts
    """
    installed_charts = []

    # split helm_list_output by 'new line'
    installed_helm_stdout = helm_list_output.split("\n")

    # Perform validation on stdout of first (0) line
    first_line_stdout = installed_helm_stdout[0].split("\t")
    if first_line_stdout[0].strip() != 'NAME' or first_line_stdout[6].strip() != 'NAMESPACE':
        raise Exception("'helm list' command output changed, probably due to helm version update, "
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
            temp_dictionary.update({'name_space': chart_details[6].strip()})
            # Update final array with the temp array of dicts of current helm deployment
            installed_charts.append(temp_dictionary)

    return installed_charts


def identify_charts_in_search(repository_name):
    """
    Execute 'helm repo update', and 'helm search repository_name' command on input values

    :param repository_name: name of repository as strings
    :return: return code and value from execution command decoded string
    """

    # Update helm repo before installation
    # --strict will fail on update warnings
    # TODO repo update will fail even if one of the repositories returned error,
    # feature requested at https://github.com/helm/helm/issues/5127
    # Add '--strict' and '--repo-name' if helm api is updated
    completed_process_object = run(["helm", "repo", "update"], stdout=PIPE, stderr=PIPE)
    if completed_process_object.returncode != 0:
        return {'status': completed_process_object.returncode,
                'value': completed_process_object.stderr.decode('utf-8').strip()}

    # execute and get CompletedProcess object
    completed_process_object = run(["helm", "search", repository_name], stdout=PIPE, stderr=PIPE)

    # If return code is not 0
    if completed_process_object.returncode:
        return {'status': completed_process_object.returncode,
                'value': completed_process_object.stderr.decode('utf-8').strip()}
    else:
        return {'status': completed_process_object.returncode,
                'value': completed_process_object.stdout.decode('utf-8').strip()}


def parse_helm_search_output(helm_search_output):
    # split stdout of helm_search_output by 'new line'
    helm_search_rows_list = helm_search_output.split("\n")

    # Perform validation on stdout of first (0) line
    first_line_stdout = helm_search_rows_list[0].split("\t")
    if first_line_stdout[0].strip() != 'NAME' or first_line_stdout[3].strip() != 'DESCRIPTION':
        raise Exception("'helm search' command output changed, probably due to helm version update, "
                        "code change is needed to resolve this issue, "
                        "contact the developer.")

    charts_list = []
    # for every line in helm search repo output, excluding the headers line (NAME, CHART VERSION etc)
    for line in helm_search_rows_list[1:]:
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

    return charts_list

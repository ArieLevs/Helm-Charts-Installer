
import subprocess
import os
import sys
import urwid
import shutil
from pathlib import Path

supported_helm_deployments = [
    {'chart_name': 'ingress-traefik',
     'helm_repo_name': 'stable/traefik',
     'name_space': 'ingress-traefik',
     'values_file': 'values_files/ingress-traefik/values.local.yml'},

    {'chart_name': 'kubernetes-dashboard',
     'helm_repo_name': 'stable/kubernetes-dashboard',
     'name_space': 'kube-system',
     'values_file': 'values_files/kubernetes-dashboard/values.local.yml'},

    {'chart_name': 'nalkinscloud-nginx',
     'helm_repo_name': 'nalkinscloud/nalkinscloud-nginx',
     'name_space': 'nalkinscloud-nginx',
     'values_file': 'values_files/nalkinscloud-nginx/values.local.yml'},

    {'chart_name': 'jenkins',
     'helm_repo_name': 'stable/jenkins',
     'name_space': 'jenkins',
     'values_file': 'values_files/jenkins/values.local.yml'},
]


def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, None, focus_map='reversed')


def sub_menu(caption, choices):
    contents = menu(caption, choices)

    def open_menu(button):
        return top.open_box(contents)
    return menu_button([caption, u''], open_menu)


def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button):
    response = urwid.Text([u'You chose ', button.label, u'\n'])
    done = menu_button(u'Ok', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def terminate_chosen(button):
    response = urwid.Text([u'Application will now terminate!'])
    done = menu_button(u'Ok', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def exit_program(button):
    raise urwid.ExitMainLoop()


class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box):
        super(CascadingBoxes, self).__init__(urwid.SolidFill(u'/'))
        self.box_level = 0
        self.open_box(box)

    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
                                             self.original_widget,
                                             align='center', width=('relative', 80),
                                             valign='middle', height=('relative', 80),
                                             min_width=24, min_height=8,
                                             left=self.box_level * 3,
                                             right=(self.max_box_levels - self.box_level - 1) * 3,
                                             top=self.box_level * 2,
                                             bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            return super(CascadingBoxes, self).keypress(size, key)


def perform_init_checks():
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


def identify_installed_helm_charts():
    """
    Function will perform a manipulation on a string output from the 'helm list' command
    and return an array of dicts with installed chart names and namespaces as strings
    as [{'chart_name': 'some_chart_name', 'name_space': 'some_name_space'}]

    'helm list' command return example:
    NAME                	REVISION	UPDATED                 	STATUS  	CHART                     	NAMESPACE
    ingress-traefik     	2       	Thu Dec 27 19:45:01 2018	DEPLOYED	traefik-1.56.0            	ingress-traefik
    kubernetes-dashboard	11      	Sun Sep 16 11:21:24 2018	DEPLOYED	kubernetes-dashboard-0.7.3	kube-system

    by validating the first line, splitting by the tab delimiter,
    and checking that the first (0) value is 'NAME' and sixth (5) value is 'NAMESPACE'
    an exception will be raised if the structure was change by HELM developers

    :return: array of dicts with helm installations
    """
    # Execute 'helm list' command, returned as CompletedProcess
    installed_helm_completed_process = subprocess.run(["helm", "list"],
                                                      stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE)
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


def install_helm_charts(charts_array):
    """
    Perform 'helm update' command on input values
    charts_array is an array of strings as:
    ['ingress-traefik', 'kubernetes-dashboard', ...]

    installation process will iterate over the 'supported_helm_deployments' variable,
    which contains an array of dicts with all supported helm charts deployments,
    installation process will init only if 'charts_array' has a value that also exists is 'supported_helm_deployments'

    :param charts_array: array of strings
    :return: None
    """
    # Update helm repo before installation
    subprocess.run(["helm", "repo", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for deployment in supported_helm_deployments:
        # Only if current chart name exists in the input 'charts_array'
        if deployment['chart_name'] in charts_array:
            subprocess.run(["helm", "upgrade", deployment['chart_name'],
                            "--install", deployment['helm_repo_name'],
                            "--namespace", deployment['name_space'],
                            "-f", deployment['values_file']],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)


def delete_helm_installations(charts_array):
    """
    Preform 'helm delete' command on input values
    charts_array is an array of strings as:
    ['ingress-traefik', 'kubernetes-dashboard', ...]

    :param charts_array: array of strings
    :return: None
    """
    for installation in charts_array:
        subprocess.run(["helm", "delete", "--purge", installation],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)


menu_top = menu(u'Main Menus', [
    sub_menu(u'Install Helm Charts', [
        sub_menu(u'Accessories', [
            menu_button(u'Text Editor', item_chosen),
            menu_button(u'Terminal', install_helm_charts),
        ]),
        menu_button(u'Terminate Application', terminate_chosen),
    ]),
    sub_menu(u'Remove Helm Charts', [
        sub_menu(u'Preferences', [
            menu_button(u'Appearance', item_chosen),
        ]),
        menu_button(u'Terminate Application', terminate_chosen),
    ]),
    menu_button(u'Terminate Application', terminate_chosen),
])

top = CascadingBoxes(menu_top)


def main():
    print("Starting applications, please wait...")
    perform_init_checks()

    #delete_helm_installations(['nalkinscloud-nginx'])
    install_helm_charts(['nalkinscloud-nginx'])
    #urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()


if __name__ == "__main__":
    main()

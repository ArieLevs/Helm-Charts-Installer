
import urwid
from os import chdir
from subprocess import run, PIPE, CalledProcessError


class InstallChartsMenu:

    def __init__(self, return_func, charts_dict_list, values_dir_path):

        self.charts_dict_list = charts_dict_list
        self.values_dir_path = values_dir_path

        self.docker_registry = ''
        self.docker_username = ''
        self.docker_password = ''

        # Define array of CheckBox, from values received from helm_charts_installed_dict
        self.selection_ch_box = [urwid.CheckBox("{:30}{}".format(chart['chart_name'], chart['name_space']))
                                 for chart in self.charts_dict_list]
        self.docker_registry_edit_box = urwid.Edit(
            ('editcp', u"Docker Registry "), self.docker_registry, align='left',
        )
        self.docker_username_edit_box = urwid.Edit(
            ('editcp', u"Docker Username "), self.docker_username, align='left',
        )
        self.docker_password_edit_box = urwid.Edit(
            ('editcp', u"Docker Password "), self.docker_password, align='left',
        )
        self.text_installation_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Helm Charts Installation"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            urwid.Padding(urwid.Text(u"Use space/enter to mark helm chart to install"), left=2, right=2, min_width=20),
            blank,

            # Display helm charts block
            urwid.Padding(
                urwid.Pile([
                    urwid.Text("    {:30}{}".format("NAME", "NAMESPACE")),
                    urwid.Pile(
                        [urwid.AttrWrap(chart, 'buttn', 'buttnf') for chart in self.selection_ch_box],
                    ),

                ]), left=2, right=2, min_width=10),
            blank,
            urwid.Padding(
                urwid.Text(
                    [u"In case chart contains ", ('important', u"docker repository secrets"), ", set the below:"]
                ), left=2, right=2, min_width=20
            ),
            urwid.Padding(urwid.AttrWrap(self.docker_registry_edit_box, 'editbx', 'editfc'), left=2, right=2),
            urwid.Padding(urwid.AttrWrap(self.docker_username_edit_box, 'editbx', 'editfc'), left=2, right=2),
            urwid.Padding(urwid.AttrWrap(self.docker_password_edit_box, 'editbx', 'editfc'), left=2, right=2),

            blank,
            urwid.Padding(
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel",
                                                 on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Install Selected Charts",
                                                 on_press=self.on_install), 'buttn', 'buttnf')
                     ],
                    20, 1, 8, 'left'),
                left=2, right=2, min_width=20, align='left'),
            blank,

            urwid.Padding(self.text_installation_result, left=2, right=2, min_width=20),
        ]

        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        self.return_func = return_func

        self.main_window = urwid.LineBox(urwid.AttrWrap(listbox, 'body'))

    def on_cancel(self, w):
        self.return_func()

    def on_install(self, w):
        charts_to_install = []
        # Iterate over all check boxes
        for selection in self.selection_ch_box:
            # If current check box selected (True)
            if selection.get_state():
                # Iterate over charts_dict_list (supported_helm_deployments)
                for supported_chart_deployment in self.charts_dict_list:
                    # If selected label exists in supported_chart_deployment
                    if selection.label.split()[0] in supported_chart_deployment['chart_name']:
                        charts_to_install.append(supported_chart_deployment)

                        if supported_chart_deployment['private_image']:
                            self.docker_registry = self.docker_registry_edit_box.edit_text
                            self.docker_username = self.docker_username_edit_box.edit_text
                            self.docker_password = self.docker_password_edit_box.edit_text

                            if self.docker_registry == '' or self.docker_username == '' or self.docker_password == '':
                                self.text_installation_result.set_text(
                                    u"One or more of the selected helm chart require docker-registry-secret, "
                                    u"All fields must be filled"
                                )
                                return

        # If the array remained empty
        if not charts_to_install:
            self.text_installation_result.set_text(u"At least one chart must be selected")
        else:
            result = self.install_helm_charts(charts_to_install)
            self.return_func(refresh_installed_charts=True, returned_result=result)
        # self.text_installation_result.set_text(u'%s' % result)

    def install_helm_charts(self, charts_list_dict):
        """
        Execute 'helm update' command on input values
        charts_list_dict is a list of dicts as:
        [
            {'chart_name': 'ingress-traefik',
            'helm_repo_name': 'stable/traefik',
            'name_space': 'ingress-traefik',
            'values_file': 'ingress-traefik.values.local.yml',
            'private_image': False},
        ]

        :param charts_list_dict: list of dicts
        :return: return code and value from execution command as dict
        """

        # Update helm repo before installation
        # --strict will fail on update warnings
        # TODO repo update will fail even if one of the repositories returned error,
        # feature requested at https://github.com/helm/helm/issues/5127
        # Add '--strict' and '--repo-name' if helm api is updated
        helm_repo_update_output = run(["helm", "repo", "update"], stdout=PIPE, stderr=PIPE)
        # If return code in not 0
        if helm_repo_update_output.returncode:
            return {'status': helm_repo_update_output.returncode,
                    'value': helm_repo_update_output.stderr.decode('utf-8').strip()}

        status = 0
        value = 'no errors found'
        for deployment in charts_list_dict:
            # execute extra commands if any, and are non empty
            if 'extra_executes' in deployment and deployment['extra_executes']:
                # Each execution is a command with args as string
                # Performing split() will create a list separated by spaces
                for execution in deployment['extra_executes']:
                    # If array is not None or empty
                    if execution:
                        try:
                            chdir(self.values_dir_path)
                            completed_process_object = run(execution.split(),
                                                           stdout=PIPE,
                                                           stderr=PIPE)

                            if completed_process_object.returncode != 0:
                                status = completed_process_object.returncode
                                value = completed_process_object.stderr.decode(
                                    'utf-8') + " *** This error occurred part of 'extra_executes' part, " \
                                               "Please make sure to resolve any error with given commands"
                                return {'status': status, 'value': value}
                        except Exception as exc:
                            return {'status': 1, 'value': str(exc)}

            # In case the deployment uses images from private repository
            # then install helm chart with setting the docker-registry secret values
            if deployment['private_image']:
                completed_process_object = run(["helm", "upgrade", deployment['chart_name'],
                                                "--install", deployment['helm_repo_name'],
                                                "--namespace", deployment['name_space'],
                                                "-f", self.values_dir_path + deployment['values_file'],
                                                "--set", "secrets.docker.registry=%s" % self.docker_registry,
                                                "--set", "secrets.docker.username=%s" % self.docker_username,
                                                "--set", "secrets.docker.password=%s" % self.docker_password],
                                               stdout=PIPE,
                                               stderr=PIPE)
            else:
                completed_process_object = run(["helm", "upgrade", deployment['chart_name'],
                                                "--install", deployment['helm_repo_name'],
                                                "--namespace", deployment['name_space'],
                                                "-f", self.values_dir_path + deployment['values_file']],
                                               stdout=PIPE,
                                               stderr=PIPE)
            # In case of a non 0 return code, update return from last iteration
            if completed_process_object.returncode != 0:
                status = completed_process_object.returncode
                value = completed_process_object.stderr.decode('utf-8') + " *** Additional errors may occurred"
        return {'status': status, 'value': value}


import urwid
from helm_charts.helm_functions import supported_helm_deployments, install_helm_charts, \
    delete_helm_installations, remove_helm_repo, add_helm_repo
# from helm_functions import supported_helm_deployments, install_helm_charts, \
#     delete_helm_installations, remove_helm_repo, add_helm_repo

docker_registry = ''
docker_username = ''
docker_password = ''


class InstallChartsMenu:

    def __init__(self, return_func):

        # Define array of CheckBox, from values received from helm_charts_installed_dict
        self.selection_ch_box = [urwid.CheckBox("{:30}{}".format(chart['chart_name'], chart['name_space']))
                                 for chart in supported_helm_deployments]
        self.docker_registry_edit_box = urwid.Edit(('editcp', u"Docker Registry "), docker_registry, align='left', )
        self.docker_username_edit_box = urwid.Edit(('editcp', u"Docker Username "), docker_username, align='left', )
        self.docker_password_edit_box = urwid.Edit(('editcp', u"Docker Password "), docker_password, align='left', )
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
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Install Selected Charts", on_press=self.on_install), 'buttn', 'buttnf')
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
        for index, chart in enumerate(self.selection_ch_box):
            if chart.get_state():
                # split() without arguments splits on whitespace, get first cell of split
                charts_to_install.append(chart.label.split()[0])

                # Since selection_ch_box is built from supported_helm_deployments,
                # they share same values on same indexes
                if supported_helm_deployments[index]['private_image']:
                    global docker_registry, docker_username, docker_password
                    docker_registry = self.docker_registry_edit_box.edit_text
                    docker_username = self.docker_username_edit_box.edit_text
                    docker_password = self.docker_password_edit_box.edit_text

                    if docker_registry == '' or docker_username == '' or docker_password == '':
                        self.text_installation_result.set_text(
                            u"One or more of the selected helm chart require docker-registry-secret, "
                            u"All fields must be filled"
                        )
                        return

        # If the array remained empty
        if not charts_to_install:
            self.text_installation_result.set_text(u"At least one chart must be selected")
        else:
            result = install_helm_charts(charts_to_install, docker_registry, docker_username, docker_password)
            self.return_func(refresh_installed_charts=True, returned_result=result)
        # self.text_installation_result.set_text(u'%s' % result)


class DeleteChartsMenu:

    def __init__(self, return_func, helm_charts_installed_dict):

        self.selection_ch_box = [urwid.CheckBox("{:30}{}".format(repo['chart_name'], repo['name_space']))
                                 for repo in helm_charts_installed_dict]

        self.text_deletion_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Helm Charts Removal"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            urwid.Padding(urwid.Text(u"Use space/enter to mark helm chart to delete"), left=2, right=2, min_width=20),
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
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Delete Selected Charts", on_press=self.on_delete), 'buttn', 'buttnf')
                     ],
                    20, 1, 8, 'left'),
                left=2, right=2, min_width=20, align='left'),
            blank,
            urwid.Padding(self.text_deletion_result, left=2, right=2, min_width=20),
        ]

        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        self.return_func = return_func

        self.main_window = urwid.LineBox(urwid.AttrWrap(listbox, 'body'))

    def on_cancel(self, w):
        self.return_func()

    def on_delete(self, w):
        charts_to_delete = []
        for chart in self.selection_ch_box:
            if chart.get_state():
                # split() without arguments splits on whitespace, get first cell of split
                charts_to_delete.append(chart.label.split()[0])
        # If the array remained empty
        if not charts_to_delete:
            self.text_deletion_result.set_text(u"At least one chart must be selected")
        else:
            result = delete_helm_installations(charts_to_delete)
            self.return_func(True)
        # self.text_installation_result.set_text(u'%s' % result)


class DeleteReposMenu:

    def __init__(self, return_func, helm_repos_installed_dict):

        self.helm_repos_installed_dict = helm_repos_installed_dict
        self.selection_ch_box = [urwid.CheckBox("{:30}{}".format(repo['repo_name'], repo['repo_url']))
                                 for repo in helm_repos_installed_dict]
        self.text_deletion_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Helm Repositories Removal"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            urwid.Padding(urwid.Text(u"Use space/enter to mark helm repo to remove"), left=2, right=2, min_width=20),
            blank,

            # Display helm repositories block
            urwid.Padding(
                urwid.Pile([
                    urwid.Text("    {:30}{}".format("NAME", "URL")),
                    urwid.Pile(
                        [urwid.AttrWrap(chart, 'buttn', 'buttnf') for chart in self.selection_ch_box],
                    ),

                ]), left=2, right=2, min_width=10),

            blank,
            urwid.Padding(
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Delete Selected Charts", on_press=self.on_delete), 'buttn', 'buttnf')
                     ],
                    20, 1, 8, 'left'),
                left=2, right=2, min_width=20, align='left'),
            blank,
            urwid.Padding(self.text_deletion_result, left=2, right=2, min_width=20),
        ]

        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        self.return_func = return_func
        self.main_window = urwid.LineBox(urwid.AttrWrap(listbox, 'body'))

    def on_cancel(self, w):
        self.return_func()

    def on_delete(self, w):
        repos_to_delete = []
        for index, chart in enumerate(self.selection_ch_box):
            # If checkbox selected (True)
            if chart.get_state():
                # Since selection_ch_box is built from helm_repos_installed_dict,
                # they share same values on same indexes
                repos_to_delete.append(self.helm_repos_installed_dict[index]['repo_name'])

        # If the array remained empty
        if not repos_to_delete:
            self.text_deletion_result.set_text(u"At least one repo must be selected")
        else:
            result = remove_helm_repo(repos_to_delete)
            self.return_func(refresh_installed_repos=True, returned_result=result)


class AddRepoMenu:

    def __init__(self, return_func):

        self.helm_repo_name_edit_box = urwid.Edit(('editcp', u"Helm repo name "), "set name", align='left', )
        self.helm_repo_url_edit_box = urwid.Edit(('editcp', u"Helm repo URL  "), "set url", align='left', )
        self.add_repo_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Add Helm Repository"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            blank,

            blank,
            urwid.Padding(urwid.AttrWrap(self.helm_repo_name_edit_box, 'editbx', 'editfc'), left=2, right=2),
            urwid.Padding(urwid.AttrWrap(self.helm_repo_url_edit_box, 'editbx', 'editfc'), left=2, right=2),
            blank,
            urwid.Padding(
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Add repository", on_press=self.on_add_repo), 'buttn', 'buttnf')
                     ],
                    20, 1, 8, 'left'),
                left=2, right=2, min_width=20, align='left'),

            blank,
            urwid.Padding(self.add_repo_result, left=2, right=2, min_width=20),
        ]

        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        self.return_func = return_func
        self.main_window = urwid.LineBox(urwid.AttrWrap(listbox, 'body'))

    def on_cancel(self, w):
        self.return_func()

    def on_add_repo(self, w):
        """
        Execute once 'Add repository' button pressed,
        init the 'add_helm_repo' function,
        update the 'text_helm_repo_installed_repositories' urwid.TEXT object
        and update 'helm_repo_change_result' urwid.TEXT object

        :return:
        """

        # Execute the 'add repo' function with relevant values, and get the 'value' return from function
        add_helm_repo_output = add_helm_repo(self.helm_repo_name_edit_box.edit_text,
                                             self.helm_repo_url_edit_box.edit_text)
        if add_helm_repo_output['status'] != 0:
            self.add_repo_result.set_text(add_helm_repo_output['value'])
        else:
            return self.return_func(refresh_added_repo=True, add_helm_repo_output=add_helm_repo_output['value'])

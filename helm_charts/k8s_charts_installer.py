
import argparse
import urwid
import urwid.raw_display
import urwid.web_display
from pathlib import Path
from helm_charts.helm_functions import *
from helm_charts.init_checks import init_checks
from helm_charts.kubectl_functions import *
from helm_charts.helper import *
from helm_charts.menu_install_charts import InstallChartsMenu
from helm_charts.menu_delete_charts import DeleteChartsMenu
from helm_charts.menu_delete_repos import DeleteReposMenu
from helm_charts.menu_install_repo import AddRepoMenu
# from helm_functions import *
# from init_checks import init_checks
# from kubectl_functions import *
# from helper import *
# from menu_install_charts import InstallChartsMenu
# from menu_delete_charts import DeleteChartsMenu
# from menu_delete_repos import DeleteReposMenu
# from menu_install_repo import AddRepoMenu

config_file = str(Path.home()) + "/.kube/config"
cluster_context = "docker-for-desktop"


class MainView(urwid.WidgetPlaceholder):

    def __init__(self):
        text_header = (u"Helm charts installer -  "
                       u"UP / DOWN / PAGE UP / PAGE DOWN scroll.  ctrl+e exits.")
        text_footer = remove_ansi_color_from_string(get_cluster_info().split("\n")[0])
        text_intro = [('important', u"Helm charts installer "),
                      u"installs kubernetes helm charts on a configured cluster, "
                      u"by default its intended to work on a cluster on the local host. "
                      u"For more details execute 'helm_charts -h'"]
        config_context_info = [u"Current config file:   ", ('important', config_file),
                               u"\nCurrent context used:  ", ('important', cluster_context)]

        self.helm_repo_installed_repositories_text = urwid.Text(
            identify_installed_helm_repos()['value'].replace("\t", "    "))

        self.text_helm_charts_installation_result = urwid.Text(u"", align='left')

        self.helm_repo_change_result = urwid.Text('')

        self.text_helm_charts_installed = urwid.Text(
            identify_installed_helm_charts()['value'].replace("\t", "    ")
        )

        blank = urwid.Divider()
        equal_divider = urwid.WidgetWrap(urwid.Divider("=", 1))
        asterisk_divider = urwid.WidgetWrap(urwid.Divider("*", 0, 1))
        listbox_content = [
            # Show into text
            blank,
            urwid.Padding(urwid.Text(text_intro), left=2, right=2, min_width=20),

            # Show current config file, and context used
            blank,
            urwid.Padding(urwid.Text(config_context_info), left=2, right=2, min_width=20),

            # Helm charts display
            equal_divider,
            urwid.Padding(urwid.Text([u"Installed ", ('important', u"Helm charts:")]), left=2, right=2, min_width=20),
            asterisk_divider,
            urwid.Padding(self.text_helm_charts_installed, left=2, right=2, min_width=20),
            blank,
            urwid.Padding(urwid.GridFlow(
                [urwid.AttrWrap(urwid.Button("Install Charts", self.on_chart_install_open), 'buttn', 'buttnf')],
                18, 3, 1, 'left'),
                left=2, right=2, min_width=13),
            blank,
            urwid.Padding(urwid.GridFlow(
                [urwid.AttrWrap(urwid.Button("Delete Charts", self.on_chart_delete_open), 'buttn', 'buttnf')],
                18, 3, 1, 'left'),
                left=2, right=2, min_width=13),
            blank,
            # Print results of charts installations
            urwid.Padding(self.text_helm_charts_installation_result, left=2, right=2, min_width=20),

            # Helm repositories display
            equal_divider,
            urwid.Padding(
                urwid.Text([u"Installed ", ('important', u"Helm repositories:")]), left=2, right=2, min_width=20),
            asterisk_divider,
            urwid.Padding(self.helm_repo_installed_repositories_text, left=2, right=2, min_width=20),
            blank,
            urwid.Padding(
                urwid.AttrWrap(
                    urwid.Button("Add repository", self.on_repo_add_menu_open), 'buttn', 'buttnf'),
                left=2, right=2, width=25),
            blank,
            urwid.Padding(
                urwid.AttrWrap(
                    urwid.Button("Delete repositories", self.on_repo_delete_menu_open), 'buttn', 'buttnf'),
                left=2, right=2, width=25),
            blank,
            # Print result from helm repo add
            urwid.Padding(self.helm_repo_change_result, left=2, right=2, min_width=20),
        ]

        header = urwid.AttrWrap(urwid.Text(text_header), 'header')
        footer = urwid.AttrWrap(urwid.Text(text_footer), 'footer')
        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        # Frame widget is used to keep the instructions at the top of the screen
        self.frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header, footer=footer)

        urwid.WidgetPlaceholder.__init__(self, self.frame)

    def button_press(self, button):
        self.frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')

    def on_chart_install_open(self, w):
        """
        Execute once 'Install Charts' button pressed,
        init the 'InstallChartsMenu' class, and perform an overlay to that class

        :param w:
        :return:
        """
        install_charts_menu = InstallChartsMenu(self.on_charts_menu_close, supported_helm_deployments)
        self.original_widget = urwid.Overlay(install_charts_menu.main_window, self.original_widget,
                                             align='center', width=120, valign='middle', height=30)

    def on_chart_delete_open(self, w):
        """
        Execute once 'Delete Charts' button pressed,
        init the 'DeleteChartsMenu' class, and perform an overlay to that class

        :param w:
        :return:
        """
        delete_charts_menu = DeleteChartsMenu(self.on_charts_menu_close,
                                              parse_helm_list_output(identify_installed_helm_charts()['value']))
        self.original_widget = urwid.Overlay(delete_charts_menu.main_window, self.original_widget,
                                             align='center', width=120, valign='middle', height=30)

    def on_charts_menu_close(self, refresh_installed_charts=False, returned_result=None):
        # refresh_installed_charts parameter is checked to determine if installed charts text needs update
        if refresh_installed_charts:
            self.text_helm_charts_installed.set_text(
                identify_installed_helm_charts()['value'].replace("\t", "    ")
            )
            # If this function returned with some result
            if returned_result is not None and 'status' in returned_result:
                # In case there where no errors print nothing
                if returned_result['status'] == 0:
                    self.text_helm_charts_installation_result.set_text(u"")
                else:
                    self.text_helm_charts_installation_result.set_text(("errors", returned_result['value']))
        self.original_widget = self.frame

    def on_repo_add_menu_open(self, w):
        """
        Execute once 'Add repository' button pressed,
        init the 'InstallChartsMenu' class, and perform an overlay to that class

        :param w:
        :return:
        """
        add_repo_menu = AddRepoMenu(self.on_repos_menu_closed)
        self.original_widget = urwid.Overlay(add_repo_menu.main_window, self.original_widget,
                                             align='center', width=120, valign='middle', height=30)

    def on_repo_delete_menu_open(self, w):
        """
        Execute once 'Delete repositories' button pressed,
        init the 'DeleteReposMenu' class, and perform an overlay to that class

        :param w:
        :return:
        """
        delete_repos_menus = DeleteReposMenu(self.on_repos_menu_closed,
                                             parse_helm_repo_list_output(identify_installed_helm_repos()['value']))
        self.original_widget = urwid.Overlay(delete_repos_menus.main_window, self.original_widget,
                                             align='center', width=120, valign='middle', height=30)

    def on_repos_menu_closed(self, refresh_installed_repos=False, returned_result=None):
        if refresh_installed_repos:
            # Reset the installed repos text area
            self.helm_repo_installed_repositories_text.set_text(
                identify_installed_helm_repos()['value'].replace("\t", "    ")
            )
            if returned_result is not None and 'status' in returned_result:
                # In case there where no errors print nothing
                if returned_result['status'] == 0:
                    self.helm_repo_change_result.set_text(u"")
                else:
                    self.helm_repo_change_result.set_text(("errors", returned_result['value']))
        self.original_widget = self.frame


class HelmInstaller:

    def __init__(self):

        self.frame = MainView()

    def main(self):
        if urwid.web_display.is_web_request():
            screen = urwid.web_display.Screen()
        else:
            screen = urwid.raw_display.Screen()
        urwid.MainLoop(self.frame, main_palette, screen, unhandled_input=self.unhandled).run()

    def unhandled(self, key):
        if key == 'ctrl e':
            raise urwid.ExitMainLoop()


def main():
    urwid.web_display.set_preferences("Urwid Tour")
    # try to handle short web requests quickly
    if urwid.web_display.handle_short_request():
        return

    global config_file
    global cluster_context

    parser = argparse.ArgumentParser(description='Python Helm Charts Installer')
    parser.add_argument('--config-file', help='Path to kubernetes config file, '
                                              'Default is `{}`'.format(config_file), required=False)
    parser.add_argument('--use-context', help='Cluster context name to use, '
                                              'Default is `{}`'.format(cluster_context), required=False)
    parser.add_argument('--helm-init', action='store_true', help='Perform "helm init" on cluster', required=False)

    args = vars(parser.parse_args())

    if args['config_file'] is not None:
        config_file = args['config_file']

    if args['use_context'] is not None:
        cluster_context = args['use_context']

    print("Starting application, please wait...")
    init_checks(config_file, cluster_context, args['helm_init'])

    helm_installer = HelmInstaller()
    helm_installer.main()


if __name__ == '__main__':
    main()

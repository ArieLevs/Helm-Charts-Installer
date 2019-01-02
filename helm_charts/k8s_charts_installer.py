
import argparse
import urwid
import urwid.raw_display
import urwid.web_display
from pathlib import Path
from helm_charts.helm_functions import *
from helm_charts.init_checks import init_checks
from helm_charts.kubectl_functions import *
from helm_charts.helper import *
from helm_charts.charts_menu import InstallChartsMenu, DeleteChartsMenu
# from helm_functions import *
# from init_checks import init_checks
# from kubectl_functions import *
# from helper import *
# from charts_menu import InstallChartsMenu, DeleteChartsMenu

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
            identify_installed_helm_repos(return_only_decoded_string=True).replace("\t", "    "))
        self.text_helm_charts_installation_result = urwid.Text(u"", align='left')
        # helm_repo_installed_repositories_dict = identify_installed_helm_repos()

        self.helm_repo_name_edit_box = urwid.Edit(('editcp', u"Helm repo name "), "set name", align='left', )
        self.helm_repo_url_edit_box = urwid.Edit(('editcp', u"Helm repo URL  "), "set url", align='left', )
        self.helm_repo_add_result = urwid.Text('')

        self.text_helm_charts_installed = urwid.Text(
            identify_installed_helm_charts(return_only_decoded_string=True).replace("\t", "    ")
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
                left=4, right=3, min_width=13),
            blank,
            urwid.Padding(urwid.GridFlow(
                [urwid.AttrWrap(urwid.Button("Delete Charts", self.on_chart_delete_open), 'buttn', 'buttnf')],
                18, 3, 1, 'left'),
                left=4, right=3, min_width=13),
            blank,
            urwid.Padding(self.text_helm_charts_installation_result, left=2, right=2, min_width=20),

            # Helm repositories display
            equal_divider,
            urwid.Padding(
                urwid.Text([u"Installed ", ('important', u"Helm repositories:")]), left=2, right=2, min_width=20),
            asterisk_divider,
            urwid.Padding(self.helm_repo_installed_repositories_text, left=2, right=2, min_width=20),
            blank,
            urwid.Padding(urwid.AttrWrap(self.helm_repo_name_edit_box, 'editbx', 'editfc'), left=2, right=2),
            urwid.Padding(urwid.AttrWrap(self.helm_repo_url_edit_box, 'editbx', 'editfc'), left=2, right=2),
            blank,
            urwid.Padding(
                urwid.AttrWrap(
                    urwid.Button("Add repository", self.add_repo_button_pressed), 'buttn', 'buttnf'),
                left=2, right=2, width=18),

            blank,
            urwid.Padding(self.helm_repo_add_result, left=2, right=2, min_width=20),
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

    def add_repo_button_pressed(self, button):
        """
        Execute once 'Add repository' button pressed,
        init the 'add_helm_repo' function,
        update the 'text_helm_repo_installed_repositories' urwid.TEXT object
        and update 'helm_repo_add_result' urwid.TEXT object

        :param button:
        :return:
        """

        add_helm_repo_output = add_helm_repo(self.helm_repo_name_edit_box.edit_text,
                                             self.helm_repo_url_edit_box.edit_text)['value']
        [urwid.AttrWrap(urwid.CheckBox("{:30}{}".format(txt['repo_name'], txt['repo_url'])), 'buttn', 'buttnf')
         for txt in identify_installed_helm_repos()]
        self.helm_repo_installed_repositories_text.set_text(
            identify_installed_helm_repos(return_only_decoded_string=True).replace("\t", "    ")
        )
        self.helm_repo_add_result.set_text(add_helm_repo_output)

    def on_menu_close(self, refresh_installed_charts=False, returned_result=None):
        """Return to main screen"""
        # refresh_installed_charts parameter is checked to determine if installed charts text needs update
        if refresh_installed_charts:
            self.text_helm_charts_installed.set_text(
                identify_installed_helm_charts(return_only_decoded_string=True).replace("\t", "    ")
            )
        # If this function returned with some result
        if returned_result is not None and 'status' in returned_result:
            # In case there where no errors
            if returned_result['status'] == 0:
                self.text_helm_charts_installation_result.set_text(u"")
            else:
                self.text_helm_charts_installation_result.set_text(("errors", returned_result['value']))
        self.original_widget = self.frame

    def on_docker_menu_open(self, w):
        self.original_widget = urwid.Overlay(self.docker_registry_menu.main_window, self.original_widget,
                                             align='center', width=40, valign='middle', height=10)

    def on_chart_install_open(self, w):
        """
        Execute once 'Install Charts' button pressed,
        init the 'InstallChartsMenu' class, and perform an overlay to that class

        :param w:
        :return:
        """
        install_charts_menu = InstallChartsMenu(self.on_menu_close)
        self.original_widget = urwid.Overlay(install_charts_menu.main_window, self.original_widget,
                                             align='center', width=120, valign='middle', height=30)

    def on_chart_delete_open(self, w):
        """
        Execute once 'Delete Charts' button pressed,
        init the 'InstallChartsMenu' class, and perform an overlay to that class

        :param w:
        :return:
        """
        delete_charts_menu = DeleteChartsMenu(self.on_menu_close, identify_installed_helm_charts())
        self.original_widget = urwid.Overlay(delete_charts_menu.main_window, self.original_widget,
                                             align='center', width=120, valign='middle', height=30)


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
